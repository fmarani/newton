#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import random
import asyncio
import json
import hashlib
import string
from datetime import datetime
import logging
import sys
import heapq
import newton
from newton import config
from newton import async_http
from newton.storage.errors import StorageException
from newton import twitter as tw

from . import storage

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def random_id():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))


def hash_dict(data):
    data_hashing = json.dumps(data)
    data_hash = hashlib.sha256(data_hashing.encode("utf8")).hexdigest()
    data['hash'] = data_hash


async def post_reply(replyToUrl, text):
    first_word, _ = text.split(" ", 1)
    if first_word[0] != "@":
        return False

    thing = {
            "type": "reply",
            "msg": text,
            "replyToUrl": replyToUrl,
            }

    if config.TWITTER_INTEGRATION:
        await tw.post_reply(replyToUrl, text)

    return await post_addressable_entity(thing)


async def post_renewt(renewtUrl):
    thing = {
            "type": "renewt",
            "renewtUrl": renewtUrl,
            }

    if config.TWITTER_INTEGRATION:
        await tw.post_retweet(renewtUrl)

    return await post_unaddressable_entity(thing)


async def post_like(likeUrl):
    thing = {
            "type": "like",
            "likeUrl": likeUrl,
            }

    if config.TWITTER_INTEGRATION:
        await tw.post_like(likeUrl)

    return await post_unaddressable_entity(thing)


async def post_newt(text, loop):
    newt = {
            "type": "newt",
            "msg": text,
            }

    if config.TWITTER_INTEGRATION:
        await tw.post_tweet(text)

    return await post_addressable_entity(newt)

async def post_addressable_entity(data):
    base = {
            "version": 1,
            "id": random_id(),
            "datetime": datetime.utcnow().isoformat()
            }
    data.update(base)

    with storage.write_new_resource("feed-%s.json" % data['id']) as f:
        hash_dict(data)
        data_str = json.dumps(data)
        fentry = "%s\n" % data_str
        f.write(fentry)
        url = f.url

    try:
        original_data = await storage.read_resource("feed.json")
    except StorageException:
        original_data = ""

    with storage.write_resource("feed.json") as f:
        data['url'] = url
        hash_dict(data)
        data_str = json.dumps(data)
        fentry = "%s\n" % data_str
        f.write(fentry)
        f.write(original_data)

    pushed = await push(fentry)
    return pushed


async def post_unaddressable_entity(data):
    base = {
            "version": 1,
            "id": random_id(),
            "datetime": datetime.utcnow().isoformat()
            }
    data.update(base)

    try:
        original_data = await storage.read_resource("feed.json")
    except StorageException:
        original_data = ""

    with storage.write_resource("feed.json") as f:
        hash_dict(data)
        data_str = json.dumps(data)
        fentry = "%s\n" % data_str
        f.write(fentry)
        f.write(original_data)

    pushed = await push(fentry)
    return pushed


async def push(fentry):
    if config.USER_PUSH_URLS:
        return await async_http.publish(config.USER_PUSH_URLS['PUBLISH'], fentry)


def init_profile():
    newconf = storage.init()
    handle = config.USER_HANDLE
    name = config.USER_NAME
    data = {
        "version": 1,
        "type": "profile",
        "pubKey": "tofix",
        "handle": handle,
        "name": name,
        "imageUrl": config.USER_IMAGE_URL,
        }
    if config.USER_PUSH_URLS:
        data['subscribeUrl'] = config.USER_PUSH_URLS['SUBSCRIBE']

    if newconf:
        data['feedUrl'] = storage.get_resource_link("feed.json", config=newconf)
        data['followingUrl'] = storage.get_resource_link("following.json", config=newconf)
    else:
        data['feedUrl'] = storage.get_resource_link("feed.json")
        data['followingUrl'] = storage.get_resource_link("following.json")

    if config.STORAGE_CLASS == "googledrive":
        google_fileid = newconf["profile.json"]["id"]
    else:
        google_fileid = None

    hash_dict(data)
    for_saving = json.dumps(data)

    with storage.write_resource("profile.json", google_fileid=google_fileid) as f:
        f.write(for_saving)


async def follow(user_url):
    async with storage.append_resource("following.json") as f:
        response = await async_http.fetch(user_url)
        jdata = json.loads(response.decode("utf8"))
        # FIXME: check collision
        data = {
                "version": 1,
                "type": "follow",
                "handle": jdata['handle'],
                "profileUrl": user_url,
                "feedUrl": jdata['feedUrl'],
                }
        if jdata.get('subscribeUrl'):
            data["subscribeUrl"] = jdata['subscribeUrl']

        hash_dict(data)
        f.write(json.dumps(data))
        f.write("\n")


async def get_unified_timeline(*, loop=None):
    async def hydrate(fetcher, handle):
        data = await fetcher
        for datum in data:
            datum['handle'] = handle
            datum['datetime'] = datetime.strptime(datum['datetime'], "%Y-%m-%dT%H:%M:%S.%f")
        return data

    tasks = []
    responses = []

    followers_data = await storage.read_resource("following.json")
    followers = followers_data.strip().splitlines()

    for line in followers:
        user_data = json.loads(line)
        handle = user_data['handle']
        url_feed = user_data['feedUrl']

        task = asyncio.ensure_future(hydrate(async_http.fetch_multijson(url_feed), handle), loop=loop)
        tasks.append(task)

    if config.TWITTER_INTEGRATION:
        task = asyncio.ensure_future(tw.timeline(), loop=loop)
        tasks.append(task)

    responses = await asyncio.gather(*tasks, loop=loop)
    return heapq.merge(*responses, key=lambda x: x['datetime'], reverse=True)


async def poll_timeline(subscribe_url, url_feed, handle, new_entities_q, timeout, loop):
    async def hydrate(fetcher, handle):
        data = await fetcher
        if data:
            data['handle'] = handle
            data['datetime'] = datetime.strptime(data['datetime'], "%Y-%m-%dT%H:%M:%S.%f")
        return data

    last_entity = datetime.now()
    while True:
        entity = None

        if subscribe_url:
            entity = await hydrate(async_http.fetch_json_newer_than(subscribe_url, datetime.now(), timeout=timeout), handle)
        else:
            await asyncio.sleep(3, loop=loop)
            jdata = await async_http.fetch_multijson(url_feed)
            for jdatum in jdata:
                datum = jdatum.copy()
                datum['handle'] = handle
                datum['datetime'] = datetime.strptime(datum['datetime'], "%Y-%m-%dT%H:%M:%S.%f")
                if datum['datetime'] > last_entity:
                    entity = datum

        if entity:
            logger.info("Poll received by {} {}".format(handle, entity))
            await new_entities_q.put(entity)
            last_entity = datetime.now()

        if (datetime.now() - last_entity).seconds > timeout:
            break
        else:
            await asyncio.sleep(1, loop=loop)
            logger.info("Continuing to wait for changes...")


async def poll_all_timelines(new_entities_q, timeout, loop):
    tasks = []

    followers_data = await storage.read_resource("following.json")
    followers = followers_data.strip().splitlines()

    for line in followers:
        user_data = json.loads(line)
        handle = user_data['handle']
        subscribe_url = user_data.get('subscribeUrl')
        url_feed = user_data['feedUrl']

        #loop.run_in_executor(None, poll_timeline, url_feed, handle, new_entities_q, loop)

        task = asyncio.ensure_future(poll_timeline(subscribe_url, url_feed, handle, new_entities_q, timeout, loop), loop=loop)
        tasks.append(task)

    return tasks


async def stream_reactor(new_entities_q, cb, quick_exit):
    while True:
        try:
            entity = await new_entities_q.get()
            logger.info("Reacting to {}".format(entity))
            cb(entity)
        except asyncio.QueueEmpty:
            logger.info("Queue empty. Continuing to wait for changes...")

        if quick_exit:
            break


async def stream_unified_timeline(cb, loop, quick_exit=False):
    new_entities_q = asyncio.Queue(loop=loop)
    timeout = 3 if quick_exit else 30

    tasks = await poll_all_timelines(new_entities_q, timeout, loop)
    tasks.append(stream_reactor(new_entities_q, cb, quick_exit))

    """
    if config.TWITTER_INTEGRATION:
        task = asyncio.ensure_future(tw.timeline(), loop=loop)
        tasks.append(task)
    """

    return await asyncio.gather(*tasks, loop=loop)


def print_entity(entity):
    if entity['type'] == "newt":
        print("{:%Y-%m-%d %H:%M} {} {}".format(entity['datetime'], entity['handle'], entity['msg']))
    elif entity['type'] == "renewt":
        print("{:%Y-%m-%d %H:%M} {} Renewt: {}".format(entity['datetime'], entity['handle'], entity['renewtUrl']))
    elif entity['type'] == "like":
        print("{:%Y-%m-%d %H:%M} {} Like: {}".format(entity['datetime'], entity['handle'], entity['likeUrl']))
    elif entity['type'] == "reply":
        print("{:%Y-%m-%d %H:%M} {} {} in reply to: {}".format(entity['datetime'], entity['handle'], entity['msg'], entity['replyToUrl']))
    else:
        print("skipping unrecognized msg type")


def wait_stream_timeline(loop):
    return loop.run_until_complete(stream_unified_timeline(print_entity, loop))


def wait_timeline(loop):
    future = asyncio.ensure_future(get_unified_timeline())
    responses = loop.run_until_complete(future)
    print("Timeline")
    for resp in responses:
        print_entity(resp)


def wait(*coroutines, loop):
    return loop.run_until_complete(asyncio.gather(*coroutines, loop=loop))

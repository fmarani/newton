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
    thing = {
            "type": "reply",
            "msg": text,
            "replyToUrl": replyToUrl,
            }
    return await post_addressable_entity(thing)


async def post_renewt(renewtUrl):
    thing = {
            "type": "renewt",
            "renewtUrl": renewtUrl,
            }
    return await post_unaddressable_entity(thing)


async def post_like(likeUrl):
    thing = {
            "type": "like",
            "likeUrl": likeUrl,
            }
    return await post_unaddressable_entity(thing)


async def post_newt(text):
    newt = {
            "type": "newt",
            "msg": text,
            }
    return await post_addressable_entity(newt)


async def post_addressable_entity(data):
    try:
        original_data = await storage.read_resource("feed.json")
    except StorageException:
        original_data = ""

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

    with storage.write_resource("feed.json") as f:
        data['url'] = url
        hash_dict(data)
        data_str = json.dumps(data)
        fentry = "%s\n" % data_str
        f.write(fentry)
        f.write(original_data)


async def post_unaddressable_entity(data):
    try:
        original_data = await storage.read_resource("feed.json")
    except StorageException:
        original_data = ""

    base = {
            "version": 1,
            "id": random_id(),
            "datetime": datetime.utcnow().isoformat()
            }
    data.update(base)

    with storage.write_resource("feed.json") as f:
        hash_dict(data)
        data_str = json.dumps(data)
        fentry = "%s\n" % data_str
        f.write(fentry)
        f.write(original_data)


def init(handle=None, name=None):
    newconf = storage.init()
    if not handle:
        print("Handle:")
        handle = input()
    if not name:
        print("Name:")
        name = input()
    data = {
        "version": 1,
        "type": "profile",
        "pubKey": "tofix",
        "handle": handle,
        "name": name,
        "imageUrl": None,
        }
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
        async with async_http.session() as session:
            response = await session.get(user_url)
            resp = await response.read()
            data = json.loads(resp.decode("utf8"))
            # FIXME: check collision
            data = {
                    "version": 1,
                    "handle": data['handle'],
                    "profileUrl": user_url,
                    "feedUrl": data['feedUrl'],
                    }
            hash_dict(data)
            f.write(json.dumps(data))
            f.write("\n")


async def get_unified_timeline(*, loop=None):
    async def add_handle(fetcher, handle):
        data = await fetcher
        for datum in data:
            datum['handle'] = handle
        return data

    tasks = []
    responses = []

    try:
        followers_data = await storage.read_resource("following.json")
        followers = followers_data.strip().splitlines()
    except StorageException:
        followers = []

    async with async_http.session() as session:
        for line in followers:
            user_data = json.loads(line)
            handle = user_data['handle']
            url_feed = user_data['feedUrl']

            task = asyncio.ensure_future(add_handle(async_http.fetch_multijson(url_feed, session=session), handle), loop=loop)
            tasks.append(task)

        responses = await asyncio.gather(*tasks, loop=loop)

    return heapq.merge(*responses, key=lambda x: x['datetime'], reverse=True)


def wait_timeline():
    future = asyncio.ensure_future(get_unified_timeline())
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(future)
    print("Timeline")
    for resp in responses:
        if resp['type'] == "newt":
            print("{} {} {}".format(resp['datetime'], resp['handle'], resp['msg']))
        elif resp['type'] == "renewt":
            print("{} {} Renewt: {}".format(resp['datetime'], resp['handle'], resp['renewtUrl']))
        elif resp['type'] == "like":
            print("{} {} Like: {}".format(resp['datetime'], resp['handle'], resp['likeUrl']))
        elif resp['type'] == "reply":
            print("{} {} {} in reply to: {}".format(resp['datetime'], resp['handle'], resp['msg'], resp['replyToUrl']))
        else:
            print("skipping unrecognized msg type")


def wait(coroutine):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(coroutine)

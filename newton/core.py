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

loop = asyncio.get_event_loop()

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

async def post_newt(text):
    try:
        original_data = await storage.read_resource("feed.json")
    except StorageException:
        original_data = ""

    with storage.write_resource("feed.json") as f:
        newt = {
                "version": 1,
                "id": random_id(),
                "type": "tweet",
                "tweet": text,
                "datetime": datetime.utcnow().isoformat()
                }
        hash_dict(newt)
        newt_str = json.dumps(newt)
        data = "%s\n" % newt_str
        f.write(data.encode("utf8"))
        f.write(original_data.encode("utf8"))

def init():
    newconf = storage.init()
    data = {
        "version": 1,
        "pubKey": "abc",
        "handle": "@flagZ",
        "name": "Federico M",
        "imageUrl": None,
        }

    if config.STORAGE_CLASS == "googledrive":
        google_fileid = newconf["profile.json"]["id"]
        data['feedUrl'] = newconf["feed.json"]["url"]
        data['followingUrl'] = newconf["following.json"]["url"]
    else:
        google_fileid = None
        data['feedUrl'] = config.STORAGE_LOCAL_HTTPBASE + "feed.json"
        data['followingUrl'] = config.STORAGE_LOCAL_HTTPBASE + "following.json"

    hash_dict(data)
    for_saving = json.dumps(data)

    with storage.write_resource("profile.json", google_fileid=google_fileid) as f:
        f.write(for_saving.encode("utf8"))

async def follow(user_url):
    with storage.append_resource("following.json") as f:
        async with async_http.session() as session:
            async with session.get(user_url) as response:
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
                f.write(json.dumps(data) + "\n")

async def get_timelines():
    async def add_handle(fetcher, handle):
        data = await fetcher
        for datum in data:
            datum['handle'] = handle
        return data

    tasks = []
    responses = []

    try:
        followers_data = await storage.read_resource("following.json")
        followers = followers_data.splitlines()
    except StorageException:
        followers = []

    async with async_http.session() as session:
        for line in followers:
            user_data = json.loads(line)
            handle = user_data['handle']
            url_feed = user_data['feedUrl']

            task = asyncio.ensure_future(add_handle(async_http.fetch_multijson(url_feed, session), handle))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

    return heapq.merge(*responses, key=lambda x: x['datetime'], reverse=True)

def wait_timeline():
    future = asyncio.ensure_future(get_timelines())
    responses = loop.run_until_complete(future)
    print("Timeline")
    for resp in responses:
        print("{} {} {}".format(resp['datetime'], resp['handle'], resp['tweet']))

def wait(coroutine):
    loop.run_until_complete(coroutine)

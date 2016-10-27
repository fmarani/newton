#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import random
from aiohttp import ClientSession
from aiohttp.errors import ClientError
import asyncio
import json
import hashlib
import string
from datetime import datetime
import logging
import sys

logger = logging.getLogger(__name__)
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

def post_newt(text):
    try:
        with open("feed.json", 'r') as f:
            original_data = f.read()
    except FileNotFoundError:
        original_data = ""
    with open("feed.json", 'w') as f:
        newt = {
                "version": 1,
                "id": random_id(),
                "type": "tweet",
                "tweet": text,
                "datetime": datetime.utcnow().isoformat(),
                "location": {
                    "lat": 0.0,
                    "lng": 12.0,
                    }}
        hash_dict(newt)
        newt_str = json.dumps(newt)
        f.write("%s\n" % newt_str)
        f.write(original_data)

def init():
    data = {
        "version": 1,
        "pubKey": "abc",
        "handle": "@flagZ",
        "name": "Federico M",
        "imageUrl": None,
        }
    hash_dict(data)
    for_saving = json.dumps(data)
    with open("profile.json", 'w') as f:
        f.write(for_saving)

async def hello():
    async with ClientSession() as session:
        async with session.get("http://httpbin.org/headers") as response:
            response = await response.read()
            print(response)

async def follow(user_url):
    with open("following.json", 'a') as f:
        async with ClientSession() as session:
            async with session.get(user_url + "profile.json") as response:
                resp = await response.read()
                handle = json.loads(resp.decode("utf8"))['handle']
                # FIXME: check collision
                data = {
                        "version": 1,
                        "handle": handle,
                        "baseUrl": user_url
                        }
                hash_dict(data)
                f.write(json.dumps(data) + "\n")

async def fetch(url, session):
    logger.info("requesting %s" % url)
    try:
        async with session.get(url) as response:
            return await response.read()
    except ClientError:
        return None

async def get_timelines():
    tasks = []

    with open("following.json", 'r') as f:
        async with ClientSession() as session:
            for line in f.readlines():
                user_data = json.loads(line)
                url_feed = user_data['baseUrl'] + "feed.json"

                task = asyncio.ensure_future(fetch(url_feed, session))
                tasks.append(task)

                responses = await asyncio.gather(*tasks)
    return responses

def timeline():
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_timelines())
    responses = loop.run_until_complete(future)
    print(responses)

def wait_follow():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(follow("http://localhost:8001/"))


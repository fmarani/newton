import logging
import json
from aiohttp import ClientSession
from aiohttp.errors import ClientError

logger = logging.getLogger()
session = None


class AsyncHttpException(Exception):
    pass


def init():
    global session
    session = ClientSession()


async def fetch(url):
    logger.info("requesting %s" % url)
    try:
        response = await session.get(url)

        if response.status != 200:
            return False
        else:
            return await response.read()
    except ClientError:
        return None


async def fetch_json_newer_than(url, last_modified, timeout=0):
    logger.info("requesting %s" % url)
    headers = {"if-modified-since": last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')}
    try:
        response = await session.get(url, headers=headers, timeout=timeout)

        if response.status != 200:
            return False
        else:
            fetched = await response.read()
            return json.loads(fetched.decode("utf8"))
    except ClientError:
        return None


async def fetch_multijson(url):
    fetched = await fetch(url)
    if fetched:
        data = fetched.decode("utf8").splitlines()
        return [json.loads(i) for i in data]
    else:
        return []


async def publish(url, data):
    logger.info("publish %s" % url)
    try:
        response = await session.post(url, data=data)
        logger.info("publish resp: {}".format(await response.read()))

        if response.status != 200:
            return False
        else:
            return True
    except ClientError:
        return None


def destroy():
    session.close()

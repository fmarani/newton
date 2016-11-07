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
        return await response.read()
    except ClientError:
        return None


async def fetch_multijson(url):
    fetched = await fetch(url)
    data = fetched.decode("utf8").splitlines()
    return [json.loads(i) for i in data]


def destroy():
    session.close()

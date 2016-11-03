import logging
import json
from aiohttp import ClientSession
from aiohttp.errors import ClientError

logger = logging.getLogger()
session = ClientSession

class AsyncHttpException(Exception):
    pass

async def fetch(url, *, session=None):
    logger.info("requesting %s" % url)
    try:
        if not session:
            async with ClientSession() as session:
                response = await session.get(url)
                return await response.read()
        else:
            response = await session.get(url)
            return await response.read()
    except ClientError:
        return None

async def fetch_multijson(url, *, session=None):
    fetched = await fetch(url, session=session)
    data = fetched.decode("utf8").splitlines()
    return [json.loads(i) for i in data]

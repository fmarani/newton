from newton import config
from newton.core import wait, post_newt, follow, get_unified_timeline, init
from aiohttp import web
import pytest
from aiohttp.test_utils import TestClient as TClient
from unittest.mock import patch


def webserver(loop):
    app = web.Application(loop=loop)
    app.router.add_static("/", config.STORAGE_LOCAL_PATH)
    return app


def setup_module():
    config.setup("config_test")
    # todo: RESET folder
    init("@test", "Test Test")


async def test_post_newt_and_follow_yourself_reads_back_in_timeline(loop):
    app = webserver(loop)
    client = lambda: TClient(app)

    async with client() as session:
        response = await session.get("/profile.json")
        resp = await response.read()
        print(resp)

    with patch("newton.async_http.session", client):
        await follow("/profile.json")
        await post_newt("test")
        timeline = list(await get_unified_timeline(loop=loop))
        assert len(timeline) == 1
        assert timeline[0]['msg'] == "test"

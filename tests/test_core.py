from newton import config
from newton.core import post_newt, follow, get_unified_timeline, init_profile
from aiohttp import web
import pytest
from aiohttp.test_utils import TestClient, TestServer
from unittest.mock import patch
import tempfile
import shutil


def make_app(loop):
    app = web.Application(loop=loop)
    app.router.add_static("/", tmppath)
    return app


def setup_module():
    global tmppath
    tmppath = tempfile.mkdtemp()

    config.setup("config_test")
    config.override("STORAGE_LOCAL_PATH", tmppath)

    init_profile()

def teardown_module():
    shutil.rmtree(tmppath)

async def test_post_newt_and_follow_yourself_reads_back_in_timeline(loop):
    async with TestServer(make_app(loop)) as ts:
        client = TestClient(ts)
        with patch("newton.async_http.session", client):
            await follow("/profile.json")
            await post_newt("test", loop=loop)
            timeline = list(await get_unified_timeline(loop=loop))
            assert len(timeline) == 1
            assert timeline[0]['msg'] == "test"

from newton import config
from newton.core import post_newt, follow, get_unified_timeline, init_profile, stream_unified_timeline
from aiohttp import web
import pytest
from aiohttp.test_utils import TestClient as TClient, TestServer as TServer
from unittest.mock import patch
import tempfile
import shutil
import queue


async def publish(request):
    thing = await request.read()
    request.app['queue'].put(thing.decode("utf8"))
    return web.Response()


async def subscribe(request):
    try:
        thing = request.app['queue'].get(True, timeout=2)
        return web.Response(status=200, text=thing)
    except queue.Empty:
        return web.Response(status=304)


def make_app(loop):
    async def empty_queue_middleware(app, handler):
        async def middleware_handler(request):
            if request.path == "/feed.json":
                q = app['queue']
                with q.mutex:
                    q.queue.clear()
            return await handler(request)
        return middleware_handler
    app = web.Application(middlewares=[empty_queue_middleware], loop=loop)
    app['queue'] = queue.Queue()
    app.router.add_get("/sub", subscribe)
    app.router.add_post("/pub", publish)
    app.router.add_static("/", config.STORAGE_LOCAL_PATH)
    return app


@pytest.fixture(scope="module")
def profile(request):
    tmppath = tempfile.mkdtemp()
    config.setup("tests.config_test")
    config.override("STORAGE_LOCAL_PATH", tmppath)
    init_profile()
    yield
    shutil.rmtree(config.STORAGE_LOCAL_PATH)


@pytest.fixture(scope="module")
def profile_no_push(request):
    tmppath = tempfile.mkdtemp()
    config.setup("tests.config_test")
    config.override("STORAGE_LOCAL_PATH", tmppath)
    with config.patch("USER_PUSH_URLS", None):
        init_profile()
    yield
    shutil.rmtree(config.STORAGE_LOCAL_PATH)


async def test_post_newt_and_follow_yourself_reads_back_in_timeline(loop, profile):
    async with TServer(make_app(loop)) as ts:
        async with TClient(ts) as client:
            with patch("newton.async_http.session", client):
                await follow("/profile.json")
                posted = await post_newt("test", loop=loop)
                assert posted == True
                timeline = list(await get_unified_timeline(loop=loop))
                assert len(timeline) == 1
                assert timeline[0]['msg'] == "test"
                posted = await post_newt("test2", loop=loop)
                streamed_entities = []
                def seappend(x):
                    streamed_entities.append(x)
                await stream_unified_timeline(seappend, loop, quick_exit=True)
                assert len(streamed_entities) == 1
                assert streamed_entities[0]['msg'] == "test2"

async def test_same_without_subserver(loop, profile_no_push):
    async with TServer(make_app(loop)) as ts:
        async with TClient(ts) as client:
            with patch("newton.async_http.session", client):
                await follow("/profile.json")
                posted = await post_newt("test", loop=loop)
                assert posted == True
                timeline = list(await get_unified_timeline(loop=loop))
                assert len(timeline) == 1
                assert timeline[0]['msg'] == "test"
                posted = await post_newt("test2", loop=loop)
                streamed_entities = []
                def seappend(x):
                    streamed_entities.append(x)
                await stream_unified_timeline(seappend, loop, quick_exit=True)
                assert len(streamed_entities) == 1
                assert streamed_entities[0]['msg'] == "test2"

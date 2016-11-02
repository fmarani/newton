from newton import config
from newton.storage.errors import StorageException

from contextlib import contextmanager
import tempfile
import os

path = getattr(config, "STORAGE_LOCAL_PATH")


def init():
    if not os.path.exists(path):
        os.mkdir(path)


async def read_resource(name):
    try:
        with open(os.path.join(path, name), 'r') as f:
            return f.read()
    except FileNotFoundError as e:
        raise StorageException(e)


@contextmanager
def write_resource(name, **kwargs):
    t = tempfile.NamedTemporaryFile(mode="w", encoding="utf8", delete=False)
    t.url = get_resource_link(name)  # only for parity with googledrive:write_new_resource
    yield t
    t.close()
    os.rename(t.name, os.path.join(path, name))


write_new_resource = write_resource


class append_resource:
    def __init__(self, name, **kwargs):
        self.name = name
        self.kwargs = kwargs

    async def __aenter__(self):
        self.f = open(os.path.join(path, self.name), 'a')
        return self.f

    async def __aexit__(self, exc_type, exc, tb):
        self.f.close()


def get_resource_link(name, **kwargs):
    if 'config' in kwargs:
        conf = kwargs['config']
    else:
        conf = config

    return conf.STORAGE_LOCAL_HTTPBASE + name

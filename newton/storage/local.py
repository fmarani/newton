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
    t = tempfile.NamedTemporaryFile(delete=False)
    yield t
    t.close()
    os.rename(t.name, os.path.join(path, name))


@contextmanager
def append_resource(name):
    try:
        f = open(os.path.join(path, name), 'a')
        yield f
        f.close()
    except FileNotFoundError as e:
        raise StorageException(e)



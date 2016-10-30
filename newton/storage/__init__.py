from newton import config
from newton.storage import local, googledrive
import os

storage = {
        'local': local,
        'googledrive': googledrive
        }[config.STORAGE_CLASS]

def init():
    return storage.init()

async def read_resource(name):
    return await storage.read_resource(name)

def write_resource(name, **kwargs):
    return storage.write_resource(name, **kwargs)

def append_resource(name):
    return storage.append_resource(name)

async def backup_resources():
    if not os.path.exists("backup"):
        os.mkdir("backup")
    for resource in ["profile.json", "feed.json", "following.json"]:
        with open("backup/%s" % resource, 'w') as f:
            data = await read_resource(resource)
            f.write(data)


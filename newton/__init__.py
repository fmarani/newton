import importlib
from contextlib import contextmanager

class ConfigLoader:
    def __init__(self):
        self.container = {}

    def setup(self, config_py_path):
        self.container = importlib.import_module(config_py_path)

    def __getattr__(self, key):
        return getattr(self.container, key)

    def override(self, key, value):
        return setattr(self.container, key, value)

    @contextmanager
    def patch(self, key, value):
        oldval = getattr(self.container, key)
        setattr(self.container, key, value)
        yield
        setattr(self.container, key, oldval)


config = ConfigLoader()

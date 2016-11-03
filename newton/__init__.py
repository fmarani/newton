import importlib

class ConfigLoader:
    def __init__(self):
        self.container = {}

    def setup(self, config_py_path):
        self.container = importlib.import_module(config_py_path)

    def __getattr__(self, key):
        return getattr(self.container, key)


config = ConfigLoader()

import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
location = lambda x: os.path.join(BASE_DIR, x)

STORAGE_CLASS = "local"
#STORAGE_CLASS = "googledrive"
STORAGE_LOCAL_PATH = location("output")
STORAGE_LOCAL_HTTPBASE = "http://localhost:8001/"

GOOGLEDRIVE_CLIENTSECRET = location("client_secret.json")
GOOGLEDRIVE_JSONFILES = {
        'profile.json': {'url': 'https://docs.google.com/uc?id=0B-69O3zc5rZWbWlqeVhFSERfYkU&export=download', 'id': '0B-69O3zc5rZWbWlqeVhFSERfYkU'}, 'feed.json': {'url': 'https://docs.google.com/uc?id=0B-69O3zc5rZWQjM5UmNRLURrUDA&export=download', 'id': '0B-69O3zc5rZWQjM5UmNRLURrUDA'}, 'following.json': {'url': 'https://docs.google.com/uc?id=0B-69O3zc5rZWaEs5d0t1bElESDg&export=download', 'id': '0B-69O3zc5rZWaEs5d0t1bElESDg'}}

import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
location = lambda x: os.path.join(BASE_DIR, x)

STORAGE_CLASS = "local"
#STORAGE_CLASS = "googledrive"
STORAGE_LOCAL_PATH = location("output")
STORAGE_LOCAL_HTTPBASE = "http://localhost:8001/"

GOOGLEDRIVE_CLIENTSECRET = location("client_secret.json")
GOOGLEDRIVE_JSONFILES = {
        'following.json': {'id': '0B-69O3zc5rZWZG5ITnV3RnpWalU', 'url': 'https://docs.google.com/uc?id=0B-69O3zc5rZWZG5ITnV3RnpWalU&export=download'}, 'profile.json': {'id': '0B-69O3zc5rZWLUdUQ3hnMXpKYzg', 'url': 'https://docs.google.com/uc?id=0B-69O3zc5rZWLUdUQ3hnMXpKYzg&export=download'}, 'feed.json': {'id': '0B-69O3zc5rZWS0N3M2ZCLVNhNTQ', 'url': 'https://docs.google.com/uc?id=0B-69O3zc5rZWS0N3M2ZCLVNhNTQ&export=download'}}

TWITTER_INTEGRATION = True
TWITTER_USER_CREDENTIALS = {}
TWITTER_APP_CREDENTIALS = {
        'CONSUMER_KEY': "n4Gmx0GnEFlH1mxOsYnmwHuI4",
        'CONSUMER_SECRET': "VfLQMrJpK7ovWjIzgriQC8omOfqQzs94gDj7b5YZaEeSnGtmIy",
        }

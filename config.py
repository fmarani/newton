import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
location = lambda x: os.path.join(BASE_DIR, x)

USER_HANDLE = "flagZ"
USER_NAME = "Federico M"
USER_IMAGE_URL = "http://domain/test.png"
USER_PUSH_URLS = {
        'PUBLISH': "http://localhost:8001/pub",
        'SUBSCRIBE': "http://localhost:8001/sub"
        }

STORAGE_CLASS = "local"
#STORAGE_CLASS = "googledrive"
STORAGE_LOCAL_PATH = location("output")
STORAGE_LOCAL_HTTPBASE = "http://localhost:8001/"

GOOGLEDRIVE_CLIENTSECRET = location("client_secret.json")
GOOGLEDRIVE_JSONFILES = {
        'following.json': {'id': '0B-69O3zc5rZWZG5ITnV3RnpWalU', 'url': 'https://docs.google.com/uc?id=0B-69O3zc5rZWZG5ITnV3RnpWalU&export=download'}, 'profile.json': {'id': '0B-69O3zc5rZWLUdUQ3hnMXpKYzg', 'url': 'https://docs.google.com/uc?id=0B-69O3zc5rZWLUdUQ3hnMXpKYzg&export=download'}, 'feed.json': {'id': '0B-69O3zc5rZWS0N3M2ZCLVNhNTQ', 'url': 'https://docs.google.com/uc?id=0B-69O3zc5rZWS0N3M2ZCLVNhNTQ&export=download'}}

TWITTER_INTEGRATION = True
TWITTER_USER_CREDENTIALS = {
        'ACCESS_TOKEN': '795595306511568896-OGB2IVNdqxLpM5zbHzouilVyQo4V3kW', 'ACCESS_TOKEN_SECRET': '8GvuEz9JmxHBA8JGOR7hQR0o2Nc8gmMRAvV6TFeRgsFEz'}
TWITTER_APP_CREDENTIALS = {
        'CONSUMER_KEY': "n4Gmx0GnEFlH1mxOsYnmwHuI4",
        'CONSUMER_SECRET': "VfLQMrJpK7ovWjIzgriQC8omOfqQzs94gDj7b5YZaEeSnGtmIy",
        }

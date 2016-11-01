import httplib2
import os

from apiclient import discovery, http as apihttp
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from newton import config
from newton.storage.errors import StorageException
from newton.async_http import fetch
from contextlib import contextmanager
import tempfile
import logging

# If modifying these scopes, delete your previously saved credentials
SCOPES = 'https://www.googleapis.com/auth/drive.file'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Newton'

logger = logging.getLogger()

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'newton.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials

def upload_file(file_path, file_name, file_id):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v2', http=http)
    media_body = apihttp.MediaFileUpload(file_path, mimetype='text/json', resumable=True)
    body = {
        'title': file_name,
        'description': 'backup',
        'mimeType': 'text/json',
    }

    # Permissions body description: anyone who has link can upload
    # Other permissions can be found at https://developers.google.com/drive/v2/reference/permissions
    permissions = {
        'role': 'reader',
        'type': 'anyone',
        'value': None,
        'withLink': True
    }

    if file_id:
        file = drive_service.files().update(fileId=file_id, body=body, media_body=media_body).execute()
    else:
        file = drive_service.files().insert(body=body, media_body=media_body).execute()
        drive_service.permissions().insert(fileId=file['id'], body=permissions).execute()

    file = drive_service.files().get(fileId=file['id']).execute()
    download_url = file.get('webContentLink')
    return file['id'], download_url

def init():
    with tempfile.NamedTemporaryFile() as f:
        # google drive does not accept empty files
        f.write(b"{}")
        f.flush()

        profile = upload_file(f.name, "profile.json", None)
        feed = upload_file(f.name, "feed.json", None)
        following = upload_file(f.name, "following.json", None)
        conf = {
                'profile.json': {'id': profile[0], 'url': profile[1]},
                'feed.json': {'id': feed[0], 'url': feed[1]},
                'following.json': {'id': following[0], 'url': following[1]}
                }

        print(conf)

    print("Please write this data in the config file")
    return conf

async def read_resource(name):
    url = config.GOOGLEDRIVE_JSONFILES[name]['url']
    logger.info("Reading resource from Google drive - name %s, url %s", name, url)
    data = await fetch(url)
    if data == b"{}":
        return ""
    return data.decode("utf8")

@contextmanager
def write_resource(name, **kwargs):
    t = tempfile.NamedTemporaryFile(delete=False)
    yield t
    t.close()

    if 'google_fileid' in kwargs:
        idfile = kwargs['google_fileid']
    else:
        idfile = config.GOOGLEDRIVE_JSONFILES[name]['id']

    logger.info("Writing resource to Google drive - name %s, idfile %s", name, idfile)
    upload_file(t.name, name, idfile)

@contextmanager
def write_new_resource(name, **kwargs):
    t = tempfile.NamedTemporaryFile(delete=False)

    # create an empty file with url remotely
    t.write(b"{}")
    t.flush()
    idfile, url = upload_file(t.name, name)
    t.url = url
    t.seek(0)

    yield t
    t.close()

    logger.info("Writing new resource to Google drive - name %s", name)
    upload_file(t.name, name, idfile)

def get_resource_link(name, **kwargs):
    if 'config' in kwargs:
        config = kwargs['config'] 

    return config[name]['url']

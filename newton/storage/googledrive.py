import httplib2
import os

from apiclient import discovery, http as apihttp
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
SCOPES = 'https://www.googleapis.com/auth/drive.file'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Newton'


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

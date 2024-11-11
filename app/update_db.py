from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import os
import io

from settings import (
        SERVICE_ACCOUNT_FILE,
        SCOPES,
        FOLDER_ID
    )

from errors import *

def authenticate_google_drive():
    if os.path.isfile(SERVICE_ACCOUNT_FILE):
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    else:
        raise ValueError("SERVICE_ACCOUNT_FILE not found.")

    return build('drive', 'v3', credentials=creds)

def download_from_drive(file_name, folder_id, destination_path):
    service = authenticate_google_drive()

    query = f"name='{file_name}' and '{folder_id}' in parents"
    results = service.files().list(q=query, fields='files(id)').execute()
    items = results.get('files', [])

    if items:
        file_id = items[0]['id']
        request = service.files().get_media(fileId=file_id)

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()

        with open(destination_path, 'wb') as f:
            fh.seek(0)
            f.write(fh.read())
    else:
        raise ValueError(f"{file_name} not found in folder with ID: {folder_id}.")

db_path = os.path.join(os.path.dirname(__file__), 'data', 'posts.db')
download_from_drive('posts.db', FOLDER_ID, db_path)

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload

import requests
from datetime import datetime, timezone
import logging
import re
import os
import io

from app.settings import (
        USER_AGENT,
        INITIAL_PARAMS,
        SERVICE_ACCOUNT_FILE,
        SCOPES,
        FOLDER_ID
    )

from app.database import Session
from app.models import Post
from app.errors import *
from app.api_token import get_token_access

def authenticate_google_drive():
    if os.path.isfile(SERVICE_ACCOUNT_FILE):
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    else:
        raise ValueError("SERVICE_ACCOUNT_FILE not found.")

    return build('drive', 'v3', credentials=creds)

def upload_to_drive(file_path, folder_id):
    service = authenticate_google_drive()
    file_name = 'posts.db'

    query = f"name='{file_name}' and '{folder_id}' in parents"
    results = service.files().list(q=query, fields='files(id)').execute()
    items = results.get('files', [])

    if items:
        file_id = items[0]['id']
        media = MediaFileUpload(file_path, mimetype='application/octet-stream')

        file = service.files().update(fileId=file_id, media_body=media).execute()
        logger.info(f'Arquivo {file_name} atualizado com ID: {file.get("id")}')
    else:
        raise ValueError(f"{file_name} not found in folder with ID: {folder_id}.")

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
            logger.info(f"Download {int(status.progress() * 100)}%.")

        with open(destination_path, 'wb') as f:
            fh.seek(0)
            f.write(fh.read())

        logger.info(f'Arquivo {file_name} baixado com sucesso para {destination_path}.')
    else:
        raise ValueError(f"{file_name} not found in folder with ID: {folder_id}.")

def set_request_headers(user_agent):
    headers = {'User-Agent': user_agent}
    try:
        token = get_token_access(headers=headers, params=INITIAL_PARAMS)
    except RequestError as e:
        raise RequestError(f"{e}") from e
    except APITokenError as e:
        raise APITokenError(f"{e}") from e
    headers['Authorization'] = f'bearer {token}'
    return headers

def get_subreddit_posts(subreddit, headers):
    url = f'https://oauth.reddit.com/r/{subreddit}/new?limit=100'
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise SubredditPostsError(f"Erro ao obter posts: {response.status_code} - {response.text}")

    return response.json()

def check_for_word(title, search_phrase='mbl'):
    try:
        return int(bool(re.search(r'\b' + re.escape(search_phrase) + r'\b', title, re.IGNORECASE)))
    except Exception as e:
        raise WordCheckError("Erro ao verificar palavras no título.") from e

def get_raw_data(posts, subreddit):
    try:
        new_posts = []
        for post in posts['data']['children']:
            ts = post['data']['created']
            title = post['data']['title']
            has_label = check_for_word(title)

            new_posts.append(Post(
                ts=ts,
                title=title,
                has_label=has_label,
                created_at=datetime.fromtimestamp(ts, tz=timezone.utc),
                subreddit=subreddit
            ))
        return new_posts
    except Exception as e:
        raise DataFrameCreationError(f"Erro ao criar dados a partir dos posts: {e}") from e

def insert_data_to_db(posts, db_path):
    with Session() as session:
        existing_timestamps = set(post.ts for post in session.query(Post.ts).all())

        new_posts = [post for post in posts if post.ts not in existing_timestamps]

        if new_posts:
            logging.info(f"DADOS CAPTURADOS COM SUCESSO.")
            try:
                session.add_all(new_posts)
                session.commit()
                upload_to_drive(db_path, FOLDER_ID)
            except Exception as e:
                session.rollback()
                raise DatabaseInsertError(f"[DatabaseInsertError]: {e}") from e
            else:
                logging.info(f"POSTS ENVIADOS: {len(new_posts)}")

def apply_extraction(subreddit):
    try:
        headers = set_request_headers(USER_AGENT)
        posts = get_subreddit_posts(subreddit, headers)
        new_posts = get_raw_data(posts, subreddit)
        return new_posts
    except Exception as e:
        logging.error(f"[MAIN]: {e}")

def main():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'posts.db')
    subs = ['brasil', 'brasilivre']

    for sub in subs:
        new_posts = apply_extraction(sub)
        try:
            insert_data_to_db(new_posts, db_path)
        except Exception as e:
            logging.error(f"[MAIN]: {e}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] - [%(levelname)s] - %(message)s'
    )
    logger = logging.getLogger(__name__)
    main()
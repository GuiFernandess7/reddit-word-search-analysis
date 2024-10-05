from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import requests
from datetime import datetime, timezone
import logging
import re

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
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def upload_to_drive(file_path):
    service = authenticate_google_drive()
    file_name = 'posts.db'

    query = f"name='{file_name}' and '{FOLDER_ID}' in parents"
    results = service.files().list(q=query, fields='files(id)').execute()
    items = results.get('files', [])

    if items:
        file_id = items[0]['id']
        media = MediaFileUpload(file_path, mimetype='application/x-sqlite3')

        file = service.files().update(fileId=file_id, media_body=media).execute()
        logger.info(f'Arquivo {file_name} atualizado com ID: {file.get("id")}')
    else:
        raise ValueError("posts.db not found in folder.")

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

def get_raw_data(posts):
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
                created_at=datetime.fromtimestamp(ts, tz=timezone.utc)
            ))
        return new_posts
    except Exception as e:
        raise DataFrameCreationError(f"Erro ao criar dados a partir dos posts: {e}") from e

def insert_data_to_db(posts):
    with Session() as session:
        existing_timestamps = set(post.ts for post in session.query(Post.ts).all())

        new_posts = [post for post in posts if post.ts not in existing_timestamps]

        if new_posts:
            try:
                session.add_all(new_posts)
                session.commit()
                upload_to_drive('./app/data/posts.db')
            except Exception as e:
                session.rollback()
                raise DatabaseInsertError(f"Erro ao inserir novos dados no banco de dados: {e}") from e
        else:
            logger.debug("Nenhum novo dado para inserir.")

def main():
    try:
        headers = set_request_headers(USER_AGENT)
        subreddit = 'brasilivre'
        posts = get_subreddit_posts(subreddit, headers)
        new_posts = get_raw_data(posts)
    except Exception as e:
        logging.error(f"Erro: {e}")
    else:
        logging.info(f"DADOS CAPTURADOS COM SUCESSO.")
        try:
            insert_data_to_db(new_posts)
        except Exception as e:
            logging.error(f"Erro associado ao DB: {e}")
        else:
            logging.info(f"DADOS ENVIADOS COM SUCESSO.")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    main()
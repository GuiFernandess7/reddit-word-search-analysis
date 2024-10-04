import requests
import pandas as pd
import re

from app.settings import USER_AGENT, INITIAL_PARAMS
from app.database import engine, Session
from app.models import Post
from app.errors import *
from app.api_token import get_token_access

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

def get_raw_df(posts):
    try:
        data = {
            post['data']['created']: post['data']['title']
            for post in posts['data']['children']
        }
        df = pd.DataFrame.from_dict(data, orient='index', columns=['title'])
        df['has_label'] = df['title'].apply(check_for_word)
        df['created_at'] = pd.to_datetime(df.index, unit='s')
        df.index.name = 'ts'
        return df
    except Exception as e:
        raise DataFrameCreationError(f"Erro ao criar DataFrame a partir dos posts: {e}") from e

def add_to_database(batch):
    with Session() as session:
        existing_timestamps = set(post.ts for post in session.query(Post.ts).all())
        new_data = batch[~batch.index.isin(existing_timestamps)]

        if not new_data.empty:
            try:
                new_data.to_sql('posts', engine, if_exists='append')
                print(f"{len(new_data)} novos dados inseridos.")
            except Exception as e:
                raise DatabaseInsertError(f"Erro ao inserir novos dados no banco de dados: {e}") from e
        else:
            print("Nenhum novo dado para inserir.")

def main():
    try:
        headers = set_request_headers(USER_AGENT)
        subreddit = 'brasilivre'
        posts = get_subreddit_posts(subreddit, headers)
        batch = get_raw_df(posts)
    except Exception as e:
        print(f"Erro: {e}")
    else:
        try:
            add_to_database(batch)
        except Exception as e:
            print(f"Erro associado ao DB: {e}")
        #print("tudo ok")

if __name__ == "__main__":
    main()

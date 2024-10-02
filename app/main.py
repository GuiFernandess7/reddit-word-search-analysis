import requests
import pandas as pd
import re

from app.settings import USER_AGENT, API_TOKEN
print(f"API_TOKEN: {API_TOKEN}")
from app.database import engine, Session
from app.models import Post
from app.errors import *

def set_request_headers(user_agent):
    try:
        token = API_TOKEN
        if not token:
            raise Exception("API_TOKEN não encontrado.")

        return {
            'User-Agent': user_agent,
            'Authorization': f'bearer {token}'
        }
    except Exception as e:
        raise RequestHeaderError("Falha ao configurar os headers da requisição.") from e

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
        return df
    except Exception as e:
        raise DataFrameCreationError("Erro ao criar DataFrame a partir dos posts.") from e

def get_batch_df(raw_df):
    try:
        today = pd.to_datetime("today").normalize()
        today_batch = raw_df[raw_df['created_at'].dt.date == today.date()]
        today_batch.index.name = 'ts'
        return today_batch
    except Exception as e:
        raise BatchDataFrameError("Erro ao filtrar o DataFrame para dados do dia.") from e

def add_to_database(today_batch):
    with Session() as session:
        existing_timestamps = set(post.ts for post in session.query(Post.ts).all())
        new_data = today_batch[~today_batch.index.isin(existing_timestamps)]

        if not new_data.empty:
            try:
                new_data.to_sql('posts', engine, if_exists='append')
                print(f"{len(new_data)} novos dados inseridos.")
            except Exception as e:
                raise DatabaseInsertError("Erro ao inserir novos dados no banco de dados.") from e
        else:
            print("Nenhum novo dado para inserir.")

def main():
    try:
        headers = set_request_headers(USER_AGENT)
        subreddit = 'brasilivre'
        posts = get_subreddit_posts(subreddit, headers)
        raw_df = get_raw_df(posts)
        today_batch = get_batch_df(raw_df)
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    else:
        try:
            add_to_database(today_batch)
        except Exception as e:
            print(f"Ocorreu um erro ao adicionar ao banco de dados: {e}")

if __name__ == "__main__":
    main()

import requests
import re

from app.api_token import get_token_access
from app.errors import *
from app.models.post import PostModel

from datetime import datetime, timezone

class APIAuthenticator:
    def __init__(self, user_agent, initial_params):
        self.user_agent = user_agent
        self.initial_params = initial_params
        self.token = None

    def _get_token(self):
        headers = {'User-Agent': self.user_agent}
        try:
            self.token = get_token_access(headers=headers, params=self.initial_params)
        except RequestError as e:
            raise RequestError(f"{e}") from e
        except APITokenError as e:
            raise APITokenError(f"{e}") from e

    def get_authenticated_headers(self):
        if not self.token:
            self._get_token()

        headers = {'User-Agent': self.user_agent}
        headers['Authorization'] = f'bearer {self.token}'
        return headers

class RedditAPI:
    def __init__(self, user_agent, initial_params):
        self.authenticator = APIAuthenticator(user_agent, initial_params)

    def get_subreddit_posts(self, subreddit):
        headers = self.authenticator.get_authenticated_headers()
        url = f'https://oauth.reddit.com/r/{subreddit}/new?limit=100'

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SubredditPostsError(f"Erro ao obter posts: {e}")

        return response.json()

class WordChecker:
    @staticmethod
    def check_for_word(title, search_phrase='mbl'):
        try:
            return int(bool(re.search(r'\b' + re.escape(search_phrase) + r'\b', title, re.IGNORECASE)))
        except Exception as e:
            raise WordCheckError(f"Erro ao verificar palavras no título: {e}")

class RedditFacade:
    def __init__(self, user_agent, initial_params):
        self.reddit_api = RedditAPI(user_agent, initial_params)
        self.word_checker = WordChecker()

    def get_filtered_posts(self, subreddit, search_phrase='mbl'):
        posts = self.reddit_api.get_subreddit_posts(subreddit)
        filtered_posts = []

        for post in posts.get('data', {}).get('children', []):
            ts = post['data']['created']
            title = post['data']['title']
            has_label = self.word_checker.check_for_word(title)

            post_model = PostModel(
                ts=ts,
                title=title,
                has_label=has_label,
                created_at=datetime.fromtimestamp(ts, tz=timezone.utc),
                subreddit=subreddit
            )
            filtered_posts.append(post_model)

        return filtered_posts

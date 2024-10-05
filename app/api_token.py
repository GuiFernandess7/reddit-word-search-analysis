import requests

from app.settings import (
    CLIENT_SECRET,
    CLIENT_ID,
)
from app.errors import APITokenError, RequestError

def get_token_access(headers, params):
    try:
        auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
        response = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=params, headers=headers)

    except Exception as e:
        raise RequestError(f"[RequestError]: {e}")

    else:
        if response.status_code != 200:
            raise APITokenError(f"[StatusError]: {response.status_code}: {response.text}")

        token = response.json().get('access_token')
        if not token:
            raise APITokenError(f"Token not found: {response.json()}")

        return token


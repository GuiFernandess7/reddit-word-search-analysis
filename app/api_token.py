import requests
import pandas as pd
import re
import dotenv

from app.settings import (
    CLIENT_SECRET,
    CLIENT_ID,
)

def get_token_access(headers, params):
    try:
        auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
        response = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=params, headers=headers)
    except Exception as e:
        print(f"ERRO AO REALIZAR POST REQUEST: {e}")
        return None
    else:
        token = response.json()['access_token']

    return token

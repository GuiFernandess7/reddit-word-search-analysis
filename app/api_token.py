import requests
import pandas as pd

from app.settings import (
    CLIENT_SECRET,
    CLIENT_ID,
)
from app.errors import APITokenError

def get_token_access(headers, params):
    try:
        auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
        response = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=params, headers=headers)

        if response.status_code != 200:
            raise APITokenError(f"Falha ao capturar token de acesso: {response.text}")

        token = response.json().get('access_token')
        if not token:
            raise APITokenError("Token de acesso não encontrado na resposta.")

        return token

    except Exception as e:
        raise APITokenError(f"Erro ao capturar token de acesso: {e}")
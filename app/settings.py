import dotenv
import os
dotenv.load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
USER_AGENT = os.getenv('USER_AGENT')
API_TOKEN = os.getenv('API_TOKEN')

INITIAL_PARAMS = {
    'grant_type': 'password',
    'username': USERNAME,
    'password': PASSWORD
}
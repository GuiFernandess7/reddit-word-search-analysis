import dotenv
import os
dotenv.load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
USER_AGENT = os.getenv('USER_AGENT')

SCOPES = ['https://www.googleapis.com/auth/drive.file']

SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_CREDS')
#SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), '.creds', 'creds.json')

FOLDER_ID = "1iedDsGWCMNFQ6BlUdMLtZBVwzsMLW9dY"

INITIAL_PARAMS = {
    'grant_type': 'password',
    'username': USERNAME,
    'password': PASSWORD
}
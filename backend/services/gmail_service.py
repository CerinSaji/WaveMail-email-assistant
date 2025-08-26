from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from config import GMAIL_TOKEN_PATH

def get_gmail_service():
    creds = Credentials.from_authorized_user_file(
        GMAIL_TOKEN_PATH,
        ["https://www.googleapis.com/auth/gmail.modify"]
    )
    return build("gmail", "v1", credentials=creds)


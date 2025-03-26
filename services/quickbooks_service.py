import os
import requests
from sqlalchemy.orm import Session
from models.token import Token
from dotenv import load_dotenv
from intuitlib.client import AuthClient
from intuitlib.exceptions import AuthClientError
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
ACCOUNT_API_URL = "https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/query"
ENVIRONMENT = os.getenv("ENVIRONMENT", "sandbox")
def save_tokens_to_db(db: Session, token_data: dict):
    token = Token(
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        expires_in=token_data["expires_in"],
        realm_id=token_data["realm_id"],
        token_type=token_data["token_type"],
    )
    db.merge(token)
    db.commit()

def get_latest_token(db: Session) -> Token:
    return db.query(Token).order_by(Token.created_at.desc()).first()

def refresh_token(db, token: Token):
    auth_client = AuthClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        environment=ENVIRONMENT,
        redirect_uri=REDIRECT_URI,
    )
    auth_client.refresh_token = token.refresh_token

    try:
        auth_client.refresh_access_token()
    except AuthClientError as e:
        raise Exception(f"Failed to refresh token: {str(e)}")

    new_token_data = {
        "access_token": auth_client.access_token,
        "refresh_token": auth_client.refresh_token,
        "expires_in": auth_client.expires_in,
        "realm_id": token.realm_id,
        "token_type": "Bearer"
    }

    save_tokens_to_db(db, new_token_data)
    return get_latest_token(db)

def fetch_accounts_from_qbo(token: Token):
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
        "Content-Type": "application/text"
    }
    query = "select * from Account"
    url = ACCOUNT_API_URL.format(realm_id=token.realm_id) + f"?query={query}&minorversion=65"
    return requests.get(url, headers=headers)

import backoff
import requests
from sqlalchemy.orm import Session
from intuitlib.client import AuthClient
from intuitlib.exceptions import AuthClientError
from models.token import Token
from core.config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, ENVIRONMENT

TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
ACCOUNT_API_URL = "https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/query"

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

    try:
        auth_client.refresh(token.refresh_token)
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



@backoff.on_exception(backoff.expo, (requests.exceptions.RequestException,), max_tries=3)
def fetch_accounts_from_qbo(token: Token):
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
        "Content-Type": "application/text"
    }
    query = "select * from Account"
    url = ACCOUNT_API_URL.format(realm_id=token.realm_id) + f"?query={query}&minorversion=65"
    response = requests.get(url, headers=headers)
    return response
from sqlalchemy.orm import Session
from models.token import Token
from intuitlib.client import AuthClient
from utils.logger import get_logger
from exceptions.exeptions import raise_qbo_error
from core.config import auth_client
from intuitlib.exceptions import AuthClientError

logger = get_logger(__name__)


def get_valid_token(db: Session) -> Token:
    token = db.query(Token).order_by(Token.created_at.desc()).first()
    if not token:
        raise_qbo_error("Token not found. Please authenticate first.")
    if token.is_token_expired():
        logger.info("Access token expired. Refreshing...")
        token = refresh_token(db, token)
    return token

def get_latest_token(db: Session) -> Token:
    return db.query(Token).order_by(Token.created_at.desc()).first()

def refresh_token(db: Session, token: Token):
    print(token.refresh_token)
    try:
        auth_client.refresh(refresh_token="123456")
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


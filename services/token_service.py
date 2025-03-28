from sqlalchemy.orm import Session
from models.token import Token
from exceptions.exeptions import raise_qbo_error, raise_token_refresh_failed, raise_token_not_found
from core.config import auth_client
from intuitlib.exceptions import AuthClientError

def get_valid_token(db: Session) -> Token:
    """
    Fetches the latest token from the database and checks if it is expired.
    If expired, it refreshes the token and returns the new token.
    """
    token = db.query(Token).order_by(Token.created_at.desc()).first()
    if not token:
        raise_qbo_error("Token not found. Please authenticate first.")
    if token.is_token_expired():
        token = refresh_token(db, token)
    return token

def get_latest_token(db: Session) -> Token:
    """
    Fetches the latest token from the database.
    """
    return db.query(Token).order_by(Token.created_at.desc()).first()

def refresh_token(db: Session, token: Token) -> Token:
    """
    Refreshes the token using the refresh token.'
    """
    try:
        auth_client.refresh(refresh_token=token.refresh_token)
    except AuthClientError as e:
        raise_token_refresh_failed(str(e))

    new_token_data = {
        "access_token": auth_client.access_token,
        "refresh_token": auth_client.refresh_token,
        "expires_in": auth_client.expires_in,
        "realm_id": token.realm_id,
        "token_type": "Bearer"
    }

    save_tokens_to_db(db, new_token_data)
    return get_latest_token(db)

def save_tokens_to_db(db: Session, token_data: dict) -> None:
    """
    Saves the token data to the database."
    """
    if not token_data or not isinstance(token_data, dict) :
        raise_token_not_found("Token data is empty or invalid.")
    db.query(Token).delete()
    db.commit()
    token = Token(
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        expires_in=token_data["expires_in"],
        realm_id=token_data["realm_id"],
        token_type=token_data["token_type"],
    )
    db.merge(token)
    db.commit()


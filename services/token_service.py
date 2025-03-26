from datetime import datetime, timedelta, timezone
from models.token import Token
from sqlalchemy.orm import Session
from services.quickbooks_service import refresh_token as refresh
from utils.logger import get_logger
from exceptions.exeptions import raise_qbo_error

logger = get_logger(__name__)

def is_token_expired(token: Token) -> bool:
    expires_at = token.created_at + timedelta(seconds=token.expires_in)
    return datetime.now(timezone.utc) >= expires_at

def get_valid_token(db: Session) -> Token:
    token = db.query(Token).order_by(Token.created_at.desc()).first()
    if not token:
        raise_qbo_error("Token not found. Please authenticate first.")

    if is_token_expired(token):
        logger.info("Access token expired. Refreshing...")
        token = refresh(db, token)
    return token
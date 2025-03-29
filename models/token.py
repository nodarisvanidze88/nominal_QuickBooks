from sqlalchemy import Column, String, DateTime
from database.base import Base
from datetime import datetime, timezone, timedelta

class Token(Base):
    """
    Token model for SQLAlchemy ORM.
    Represents a token in the database.
    This model is used to store access tokens and refresh tokens for QuickBooks Online API.
    """
    __tablename__ = "tokens"
    access_token = Column(String, primary_key=True)
    refresh_token = Column(String)
    expires_in = Column(String)
    realm_id = Column(String)
    token_type = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    def is_token_expired(self) -> bool:
        if self.created_at.tzinfo is None:
            created_at = self.created_at.replace(tzinfo=timezone.utc)
        else:
            created_at = self.created_at
        expires_at = created_at + timedelta(seconds=int(self.expires_in))
        return datetime.now(timezone.utc) >= expires_at
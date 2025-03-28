from sqlalchemy import Column, String, DateTime
from database.base import Base
from datetime import datetime, timezone, timedelta

class Token(Base):
    __tablename__ = "tokens"
    access_token = Column(String, primary_key=True)
    refresh_token = Column(String)
    expires_in = Column(String)
    realm_id = Column(String)
    token_type = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    def is_token_expired(self) -> bool:
        expires_at = self.created_at + timedelta(seconds=self.expires_in)
        return datetime.now(timezone.utc) >= expires_at
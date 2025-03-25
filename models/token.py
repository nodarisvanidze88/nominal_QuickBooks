from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from database.base import Base
from datetime import datetime

class Token(Base):
    __tablename__ = "tokens"
    access_token = Column(String, primary_key=True)
    refresh_token = Column(String)
    expires_in = Column(String)
    realm_id = Column(String)
    token_type = Column(String)
    created_at = Column(DateTime, default=datetime.now(datetime.timezone.utc))

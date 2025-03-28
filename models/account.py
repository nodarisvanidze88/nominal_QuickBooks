from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from database.base import Base

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    classification = Column(String)
    currency = Column(String)
    account_type = Column(String)
    active = Column(Boolean)
    current_balance = Column(Float)
    parent_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
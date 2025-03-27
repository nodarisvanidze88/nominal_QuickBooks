from pydantic import BaseModel
from typing import Optional

class AccountOut(BaseModel):
    id: int
    name: Optional[str]
    classification: Optional[str]
    currency: Optional[str]
    account_type: Optional[str]
    active: Optional[bool]
    current_balance: Optional[float]

    class Config:
        from_attributes = True

from pydantic import BaseModel, ConfigDict
from typing import Optional

class AccountOut(BaseModel):
    """
    Account schema for output.
    """
    id: int
    name: Optional[str]
    classification: Optional[str]
    currency: Optional[str]
    account_type: Optional[str]
    active: Optional[bool]
    current_balance: Optional[float]

    model_config = ConfigDict(from_attributes=True)

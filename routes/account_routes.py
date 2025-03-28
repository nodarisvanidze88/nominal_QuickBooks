from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from database.session import get_db
from models.account import Account
from schemas.account import AccountOut
from services.quickbooks_service import fetch_accounts_from_qbo
from services.token_service import get_latest_token, refresh_token
from exceptions.exeptions import raise_token_not_found 

router = APIRouter()

@router.get("/accounts", response_model=List[AccountOut])
def sync_accounts(db: Session = Depends(get_db)):
    token = get_latest_token(db)
    if not token:
       return raise_token_not_found()
    response = fetch_accounts_from_qbo(token)

    if response.status_code == 401:
        token = refresh_token(db, token)
        response = fetch_accounts_from_qbo(token)

    if response.status_code != 200:
        return {"error": "Failed to fetch accounts", "details": response.json()}

    accounts_data = response.json().get("QueryResponse", {}).get("Account", [])

    for acc in accounts_data:
        a = Account(
            id=int(acc.get("Id")),
            name=acc.get("Name"),
            classification=acc.get("Classification"),
            currency=acc.get("CurrencyRef", {}).get("value"),
            account_type=acc.get("AccountType"),
            active=acc.get("Active", False),
            current_balance=acc.get("CurrentBalance", 0.0),
            parent_id = int(acc.get("ParentRef").get("value")) if acc.get("SubAccount") else None,
        )
        db.merge(a)
    db.commit()
    return db.query(Account).all()

@router.get("/accounts/search", response_model=List[AccountOut])
def search_accounts(
    active: Optional[bool] = Query(None),
    classification: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Account)
    if active is not None:
        query = query.filter(Account.active == active)
    if classification:
        query = query.filter(Account.classification == classification)
    return query.all()

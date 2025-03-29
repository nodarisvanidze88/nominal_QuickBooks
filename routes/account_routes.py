from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Union
from database.session import get_db
from models.account import Account
from schemas.account import AccountOut
from sqlalchemy import func
from services.quickbooks_service import sync_qbo_accounts

router = APIRouter()

@router.get("/accounts", response_model=Union[List[AccountOut], dict])
def sync_accounts(db: Session = Depends(get_db)):
    """
    Sync accounts from QuickBooks Online to the local database.
    """
    return sync_qbo_accounts(db)

@router.get("/accounts/search", response_model=List[AccountOut])
def search_accounts(
    active: Optional[bool] = Query(None),
    classification: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """"
    Search accounts by active status and classification.
    """
    query = db.query(Account)
    if active is not None:
        query = query.filter(Account.active == active)
    if classification:
        query = query.filter(Account.classification == classification)
    return query.all()

@router.get("/accounts/summary")
def get_account_balance_summary(db: Session = Depends(get_db)):
    # Dynamically fetch distinct classification values
    classifications = db.query(Account.classification).distinct().all()
    classification_list = [c[0] for c in classifications if c[0] is not None]

    summary = {}
    for classification in classification_list:
        total = (
            db.query(func.sum(Account.current_balance))
            .filter(Account.classification == classification)
            .scalar()
        )
        summary[classification] = round(total or 0.0, 2)

    return dict(sorted(summary.items(), key=lambda x: x[0]))
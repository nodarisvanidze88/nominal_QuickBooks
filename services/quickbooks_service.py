import backoff
import requests
from models.token import Token
from core.config import ACCOUNT_API_URL
from models.account import Account
from sqlalchemy.orm import Session
from services.token_service import get_latest_token, refresh_token
from exceptions.exeptions import raise_accounts_fetch_failed, raise_token_not_found, raise_invalid_account_data
from exceptions.custom_exceptions import InvalidAccountData

@backoff.on_exception(backoff.expo, (requests.exceptions.RequestException,), max_tries=3)
def fetch_accounts_from_qbo(token: Token):
    """
    Fetches accounts from QuickBooks Online using the provided token."
    """
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Accept": "application/json",
        "Content-Type": "application/text"
    }
    query = "select * from Account"
    url = ACCOUNT_API_URL.format(realm_id=token.realm_id) + f"?query={query}&minorversion=65"
    response = requests.get(url, headers=headers)
    return response

def save_accounts_to_db(db, accounts_data):
    """
    Saves the fetched accounts to the database.
    """
    if not accounts_data or not isinstance(accounts_data, list):
        raise InvalidAccountData("Accounts data is empty or invalid.")

    for acc in accounts_data:
        a = Account(
            id=int(acc.get("Id")),
            name=acc.get("Name"),
            classification=acc.get("Classification"),
            currency=acc.get("CurrencyRef", {}).get("value"),
            account_type=acc.get("AccountType"),
            active=acc.get("Active", False),
            current_balance=acc.get("CurrentBalance", 0.0),
            parent_id=int(acc.get("ParentRef").get("value")) if acc.get("SubAccount") else None,
        )
        db.merge(a)
    db.commit()

def sync_qbo_accounts(db: Session) -> list[Account]:
    token = get_latest_token(db)
    if not token:
        raise_token_not_found()

    response = fetch_accounts_from_qbo(token)

    if response.status_code == 401:
        token = refresh_token(db, token)
        response = fetch_accounts_from_qbo(token)

    if response.status_code != 200:
        raise_accounts_fetch_failed(response.json())

    accounts_data = response.json().get("QueryResponse", {}).get("Account", [])
    save_accounts_to_db(db, accounts_data)

    return db.query(Account).all()

def build_account_tree(accounts):
    account_dict = {account.id: {"id": account.id, "name": account.name, "children": []} for account in accounts}

    root_nodes = []

    for account in accounts:
        if account.parent_id:
            parent = account_dict.get(account.parent_id)
            if parent:
                parent["children"].append(account_dict[account.id])
        else:
            root_nodes.append(account_dict[account.id])

    return root_nodes

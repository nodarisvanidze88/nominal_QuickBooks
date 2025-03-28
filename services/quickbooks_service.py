import backoff
import requests
from models.token import Token
from core.config import ACCOUNT_API_URL


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
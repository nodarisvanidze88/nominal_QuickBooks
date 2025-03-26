from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from database.session import get_db
from sqlalchemy.orm import Session
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from intuitlib.exceptions import AuthClientError
from fastapi import Depends
from services.quickbooks_service import save_tokens_to_db
import os

router = APIRouter()

# Load env values
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
ENVIRONMENT = os.getenv("ENVIRONMENT", "sandbox")  # "sandbox" or "production"

auth_client = AuthClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    environment=ENVIRONMENT,
    redirect_uri=REDIRECT_URI,
)

@router.get("/", summary="Start OAuth with intuit-oauth")
def authorize():
    auth_url = auth_client.get_authorization_url(
        scopes=[Scopes.ACCOUNTING, Scopes.PAYMENT]
    )
    return RedirectResponse(auth_url)

@router.get("/callback", summary="OAuth callback using intuit-oauth")
def callback(request: Request, db: Session = Depends(get_db)):
    auth_code = request.query_params.get("code")
    realm_id = request.query_params.get("realmId")

    try:
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
    except AuthClientError as e:
        return {"error": str(e)}

    token_data = {
        "access_token": auth_client.access_token,
        "refresh_token": auth_client.refresh_token,
        "expires_in": auth_client.expires_in,
        "realm_id": auth_client.realm_id,
        "token_type": "Bearer"
    }

    save_tokens_to_db(db, token_data)

    return {"message": "Authorization successful", "realm_id": realm_id}

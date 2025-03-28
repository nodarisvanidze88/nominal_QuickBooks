from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from intuitlib.enums import Scopes
from intuitlib.exceptions import AuthClientError
from services.token_service import save_tokens_to_db
from core.config import auth_client
from database.session import get_db

router = APIRouter()

@router.get("/", summary="Start OAuth with intuit-oauth")
def authorize():
    """
    Start the OAuth process by redirecting to the authorization URL.
    Redirect to the authorization URL for the user to log in and authorize the app.
    This will initiate the OAuth flow and redirect the user to the Intuit login page.
    """
    auth_url = auth_client.get_authorization_url(
        scopes=[Scopes.ACCOUNTING, Scopes.PAYMENT]
    )
    return RedirectResponse(auth_url)

@router.get("/callback", summary="OAuth callback using intuit-oauth")
def callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle the OAuth callback from Intuit.
    This endpoint is called by Intuit after the user has authorized the app.
    """
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

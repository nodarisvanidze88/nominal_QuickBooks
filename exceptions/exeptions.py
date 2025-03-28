from fastapi import HTTPException, status

def raise_qbo_error(message: str):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"QuickBooks Error: {message}")

def raise_token_not_found():
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="QuickBooks token not found")

def raise_token_refresh_failed(details:str):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error": "Failed to refresh access token", "details": details}
    )

def raise_accounts_fetch_failed(details: str):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error": "Failed to fetch accounts", "details": details}
    )
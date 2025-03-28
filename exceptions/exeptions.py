from fastapi import HTTPException, status

def raise_qbo_error(message: str):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"QuickBooks Error: {message}")

def raise_token_not_found():
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="QuickBooks token not found")

def raise_qbo_fetch_failed(details: dict):
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail={"error": "Failed to fetch accounts from QuickBooks", "details": details},
    )

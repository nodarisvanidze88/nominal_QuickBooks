from fastapi import HTTPException

def raise_qbo_error(message: str):
    raise HTTPException(status_code=400, detail=f"QuickBooks Error: {message}")
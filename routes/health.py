from fastapi import APIRouter

router = APIRouter()

@router.get("/health", summary="Health Check")
def health():
    """
    Health check endpoint to verify if the service is running."
    """
    return {"status": "ok"}
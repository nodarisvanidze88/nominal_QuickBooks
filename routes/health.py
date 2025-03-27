from fastapi import APIRouter

router = APIRouter()

@router.get("/health", summary="Health Check")
def health():
    return {"status": "ok"}
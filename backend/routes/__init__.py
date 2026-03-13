from fastapi import APIRouter

from backend.routes.chat import router as chat_router
from backend.routes.personas import router as personas_router


router = APIRouter()
router.include_router(chat_router, prefix="/chat", tags=["chat"])
router.include_router(personas_router, prefix="/personas", tags=["personas"])


@router.get("/")
def read_root() -> dict:

    return {"message": "Historical Figure Chatbot API"}

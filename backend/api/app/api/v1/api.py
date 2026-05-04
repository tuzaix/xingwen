from fastapi import APIRouter
from app.api.v1.endpoints import auth, card, upload, report, stats

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(card.router, prefix="/card", tags=["card"])
api_router.include_router(upload.router, prefix="/image", tags=["upload"])
api_router.include_router(report.router, prefix="/report", tags=["report"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])

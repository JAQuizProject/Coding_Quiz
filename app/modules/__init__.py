from fastapi import APIRouter

from .auth.router import router as auth_router
from .quiz.router import router as quiz_router
from .ranking.router import router as ranking_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(quiz_router, prefix="/quiz", tags=["quiz"])
api_router.include_router(ranking_router, prefix="/ranking", tags=["ranking"])

__all__ = ["api_router"]

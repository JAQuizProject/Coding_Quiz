from fastapi import APIRouter
from .auth import router as auth_router
from .quiz import router as quiz_router
from .ranking import router as ranking_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(quiz_router, prefix="/quiz", tags=["quiz"])
router.include_router(ranking_router, prefix="/ranking", tags=["ranking"])

__all__ = ["router"]

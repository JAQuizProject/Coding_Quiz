from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..repositories.ranking_repository import RankingRepository
from ..services.ranking_service import RankingService

router = APIRouter()


def _get_ranking_service(db: Session = Depends(get_db)) -> RankingService:
    repo = RankingRepository(db)
    return RankingService(repo)


@router.get("/get")
async def get_ranking(
    category: str = None,
    ranking_service: RankingService = Depends(_get_ranking_service),
):
    try:
        ranking_list = await ranking_service.get_ranking(category)
        return {"message": "랭킹 조회 성공", "ranking": ranking_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"랭킹 조회 오류: {str(e)}")

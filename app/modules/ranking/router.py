from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.ranking.repository import RankingRepository
from app.modules.ranking.schemas import RankingListResponse, RankingQuery
from app.modules.ranking.service import RankingService

router = APIRouter()


def _get_ranking_service(db: Session = Depends(get_db)) -> RankingService:
    repo = RankingRepository(db)
    return RankingService(repo)


@router.get("/get", response_model=RankingListResponse)
async def get_ranking(
    query: RankingQuery = Depends(),
    ranking_service: RankingService = Depends(_get_ranking_service),
) -> RankingListResponse:
    try:
        ranking_list = await ranking_service.get_ranking(query.category, query.limit)
        return RankingListResponse(message="랭킹 조회 성공", ranking=ranking_list)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"랭킹 조회 오류: {str(e)}")

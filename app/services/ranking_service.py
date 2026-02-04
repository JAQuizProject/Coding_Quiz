from datetime import datetime
from typing import Any, Dict, List, Optional

from ..repositories.ranking_repository import RankingRepository

"""
RankingService
--------------
랭킹 관련 비즈니스 로직을 수행합니다.

기능:
- 레포지토리에서 원시 데이터를 가져와서 랭킹 순서, 날짜 포맷 등을 적용하여 API 반환 형식으로 만듭니다.
"""


class RankingService:
    def __init__(self, repo: RankingRepository):
        self.repo = repo

    async def get_ranking(
        self, category: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """랭킹 데이터를 포맷팅하여 반환합니다.

        Args:
            category (Optional[str]): 카테고리 필터
            limit (int): 반환할 최대 수

        Returns:
            List[Dict[str, Any]]: rank, username, score, category, date 형식의 리스트
        """
        rows = self.repo.fetch_ranking(category, limit)
        result = []
        for i, r in enumerate(rows):
            created_at = r.get("created_at")
            if isinstance(created_at, str):
                try:
                    created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    created_at = None

            result.append(
                {
                    "rank": i + 1,
                    "username": r.get("username"),
                    "score": r.get("score"),
                    "category": r.get("category"),
                    "date": created_at.strftime("%Y-%m-%d %H:%M")
                    if created_at
                    else "N/A",
                }
            )

        return result

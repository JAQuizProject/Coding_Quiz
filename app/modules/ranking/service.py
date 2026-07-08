from datetime import datetime
from typing import Optional

from app.modules.ranking.repository import RankingRepository
from app.modules.ranking.schemas import RankingItem


class RankingService:
    ADMARKET_CATEGORY = "ADmarket"
    ADMARKET_CATEGORY_ALIASES = {"ADmarket", "Corp", "Bidding", "Message"}

    def __init__(self, repo: RankingRepository):
        self.repo = repo

    async def get_ranking(self, category: Optional[str] = None, limit: int = 10) -> list[RankingItem]:
        """랭킹 데이터를 포맷팅하여 반환합니다."""
        rows = self.repo.fetch_ranking(category, limit)
        result: list[RankingItem] = []
        for i, r in enumerate(rows, start=1):
            created_at = r.get("created_at")
            if isinstance(created_at, str):
                try:
                    created_at = datetime.strptime(
                        created_at,
                        "%Y-%m-%d %H:%M:%S",
                    )
                except ValueError:
                    created_at = None

            result.append(
                RankingItem(
                    rank=i,
                    username=str(r.get("username") or ""),
                    score=int(r.get("score") or 0),
                    category=self._normalize_category(str(r.get("category") or "전체")),
                    date=created_at.strftime("%Y-%m-%d %H:%M") if created_at else "N/A",
                )
            )

        return result

    @classmethod
    def _normalize_category(cls, category: str) -> str:
        if category in cls.ADMARKET_CATEGORY_ALIASES:
            return cls.ADMARKET_CATEGORY
        return category

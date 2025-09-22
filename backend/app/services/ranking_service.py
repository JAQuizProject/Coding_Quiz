from datetime import datetime
from typing import Any, Dict, List, Optional

from ..repositories.ranking_repository import RankingRepository


class RankingService:
    def __init__(self, repo: RankingRepository):
        self.repo = repo

    async def get_ranking(
        self, category: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
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

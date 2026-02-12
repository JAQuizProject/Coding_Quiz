from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Score, User


class RankingRepository:
    ADMARKET_CATEGORY = "ADmarket"
    ADMARKET_CATEGORY_ALIASES = {"ADmarket", "Corp", "Bidding", "Message"}

    def __init__(self, db: Session):
        """생성자"""
        self.db = db

    def fetch_ranking(self, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """랭킹 원시 데이터를 조회합니다."""
        stmt = (
            select(
                User.username.label("username"),
                Score.score.label("score"),
                Score.category.label("category"),
                Score.created_at.label("created_at"),
            )
            .select_from(Score)
            .join(User, Score.user_id == User.id)
        )

        if category and category != "전체":
            if category == self.ADMARKET_CATEGORY:
                stmt = stmt.where(Score.category.in_(sorted(self.ADMARKET_CATEGORY_ALIASES)))
            else:
                stmt = stmt.where(Score.category == category)
        elif category == "전체":
            stmt = stmt.where(Score.category == "전체")

        stmt = stmt.order_by(Score.score.desc(), Score.created_at.asc()).limit(limit)

        rows = self.db.execute(stmt).mappings().all()
        return [dict(r) for r in rows]

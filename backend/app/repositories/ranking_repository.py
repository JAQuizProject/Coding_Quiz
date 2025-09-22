from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql import text


class RankingRepository:
    def __init__(self, db: Session):
        self.db = db

    def fetch_ranking(
        self, category: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT u.username, s.score, s.category, s.created_at
            FROM scores s
            JOIN users u ON s.user_id = u.id
        """

        params = {}
        if category and category != "전체":
            query += " WHERE s.category = :category"
            params["category"] = category
        elif category == "전체":
            query += " WHERE s.category = '전체'"

        query += " ORDER BY s.score DESC, s.created_at ASC LIMIT :limit"
        params["limit"] = limit

        rows = self.db.execute(text(query), params).fetchall()
        return [
            dict(username=r[0], score=r[1], category=r[2], created_at=r[3])
            for r in rows
        ]

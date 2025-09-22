from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql import text

"""
RankingRepository
------------------
랭킹(점수) 관련 데이터베이스 접근 로직을 담당합니다.

주요 책임:
- 특정 카테고리(또는 전체)의 상위 점수 데이터를 조회

설계 주의사항:
- SQL을 직접 사용하여 필요한 컬럼만 조회합니다.
- 반환값은 서비스 계층에서 포맷팅(랭킹 번호, 날짜 포맷 등)을 수행하도록 원시 데이터를 제공합니다.
"""


class RankingRepository:
    def __init__(self, db: Session):
        """생성자

        Args:
            db (Session): SQLAlchemy 세션
        """
        self.db = db

    def fetch_ranking(
        self, category: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """랭킹 원시 데이터를 조회합니다.

        Args:
            category (Optional[str]): 카테고리 필터. None이면 전체(카테고리 미지정) 검색.
            limit (int): 반환할 최대 행 수 (기본 10)

        Returns:
            List[Dict[str, Any]]: 각 행은 dict(username, score, category, created_at) 형태로 반환됩니다.
        """
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

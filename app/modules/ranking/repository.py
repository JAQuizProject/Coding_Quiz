from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Score, User

"""
RankingRepository
------------------
랭킹(점수) 관련 데이터베이스 접근 로직을 담당합니다.

주요 책임:
- 특정 카테고리(또는 전체)의 상위 점수 데이터를 조회

설계 주의사항:
- SQLAlchemy ORM 모델 기반으로 필요한 컬럼만 선택하여 조회합니다.
- 반환값은 서비스 계층에서 포맷팅(랭킹 번호, 날짜 포맷 등)을
  수행하도록 원시 데이터를 제공합니다.
"""


class RankingRepository:
    def __init__(self, db: Session):
        """생성자

        Args:
            db (Session): SQLAlchemy 세션
        """
        self.db = db

    def fetch_ranking(self, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """랭킹 원시 데이터를 조회합니다.

        Args:
            category (Optional[str]): 카테고리 필터. None이면 전체
                (카테고리 미지정) 검색.
            limit (int): 반환할 최대 행 수 (기본 10)

        Returns:
            List[Dict[str, Any]]: 각 행은 dict(username, score, category,
                created_at) 형태로 반환됩니다.
        """
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
            stmt = stmt.where(Score.category == category)
        elif category == "전체":
            stmt = stmt.where(Score.category == "전체")

        stmt = stmt.order_by(Score.score.desc(), Score.created_at.asc()).limit(limit)

        rows = self.db.execute(stmt).mappings().all()
        return [dict(r) for r in rows]

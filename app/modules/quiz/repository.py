from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Quiz, Score


class QuizRepository:
    def __init__(self, db: Session):
        """생성자"""
        self.db = db

    def fetch_quizzes(
        self,
        category: Optional[str] = None,
        categories: Optional[Sequence[str]] = None,
        limit: Optional[int] = None,
        random_order: bool = False,
    ) -> List[Dict[str, Any]]:
        """퀴즈 목록을 조회합니다."""
        stmt = select(
            Quiz.id.label("id"),
            Quiz.question.label("question"),
            Quiz.explanation.label("explanation"),
            Quiz.answer.label("answer"),
        )

        if categories:
            stmt = stmt.where(Quiz.category.in_(categories))
        elif category:
            stmt = stmt.where(Quiz.category == category)

        if random_order:
            stmt = stmt.order_by(func.random())

        if limit is not None:
            stmt = stmt.limit(limit)

        rows = self.db.execute(stmt).mappings().all()
        return [dict(r) for r in rows]

    def fetch_categories(self) -> List[str]:
        """퀴즈 테이블에서 사용 가능한 카테고리 목록을 조회합니다."""
        stmt = select(Quiz.category).distinct().where(Quiz.category.isnot(None), Quiz.category != "")
        categories = self.db.execute(stmt).scalars().all()
        return list(categories)

    def fetch_quizzes_by_ids(self, quiz_ids: Sequence[str]) -> Dict[str, Dict[str, Any]]:
        """quiz id 목록으로 채점용 최소 정보를 조회합니다."""
        normalized_ids = [quiz_id for quiz_id in quiz_ids if quiz_id]
        if not normalized_ids:
            return {}

        stmt = (
            select(
                Quiz.id.label("id"),
                Quiz.question.label("question"),
                Quiz.answer.label("answer"),
            )
            .where(Quiz.id.in_(normalized_ids))
        )
        rows = self.db.execute(stmt).mappings().all()
        return {str(row["id"]): dict(row) for row in rows}

    def upsert_score(
        self,
        user_id: str,
        category: str,
        score_percentage: float,
    ):
        """사용자 점수를 삽입하거나(INSERT), 기존 점수가 있으면 업데이트(UPDATE)합니다."""
        existing = self.db.query(Score).filter(Score.user_id == user_id, Score.category == category).first()

        if existing:
            # 기존 레코드가 있으면 score만 변경
            existing.score = int(score_percentage)
            self.db.commit()  # 즉시 커밋
            return "update"
        else:
            # 없으면 새 레코드를 추가
            new = Score(
                user_id=user_id,
                category=category,
                score=int(score_percentage),
            )
            self.db.add(new)
            self.db.commit()  # 즉시 커밋
            return "insert"

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql import text


class QuizRepository:
    def __init__(self, db: Session):
        self.db = db

    def fetch_quizzes(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        if category:
            query = text(
                "SELECT id, question, explanation, answer FROM quizzes WHERE category = :category"
            )
            params = {"category": category}
        else:
            query = text("SELECT id, question, explanation, answer FROM quizzes")
            params = {}

        rows = self.db.execute(query, params).fetchall()
        return [
            {"id": r[0], "question": r[1], "explanation": r[2], "answer": r[3]}
            for r in rows
        ]

    def fetch_categories(self) -> List[str]:
        rows = self.db.execute(text("SELECT DISTINCT category FROM quizzes")).fetchall()
        return [r[0] for r in rows if r[0]]

    def upsert_score(self, user_id: int, category: str, score_percentage: float):
        # Assumes Score model and transactional handling by caller
        from ..models.score import Score

        existing = (
            self.db.query(Score)
            .filter(Score.user_id == user_id, Score.category == category)
            .first()
        )
        if existing:
            existing.score = int(score_percentage)
            self.db.commit()
            return "update"
        else:
            new = Score(user_id=user_id, category=category, score=int(score_percentage))
            self.db.add(new)
            self.db.commit()
            return "insert"

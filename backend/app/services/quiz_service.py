from typing import Any, Dict, List, Optional

from ..repositories.quiz_repository import QuizRepository


class QuizService:
    def __init__(self, repo: QuizRepository):
        self.repo = repo

    async def get_quizzes(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        # simple pass-through; keep async for compatibility with async routers
        return self.repo.fetch_quizzes(category)

    async def get_categories(self) -> List[str]:
        return self.repo.fetch_categories()

    async def submit_score(self, user_id: int, score_data: dict) -> Dict[str, Any]:
        category = score_data.get("category", "전체")
        correct_count = score_data.get("correct", 0)
        total_questions = score_data.get("total", 10)
        score_percentage = (
            (correct_count / total_questions) * 100 if total_questions else 0
        )

        result = self.repo.upsert_score(user_id, category, score_percentage)
        message = (
            "기존 점수 업데이트 성공" if result == "update" else "새 점수 저장 성공"
        )
        return {"message": message, "score": score_percentage}

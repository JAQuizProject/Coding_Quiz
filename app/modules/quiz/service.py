from typing import Optional

from app.modules.quiz.grading import is_answer_accepted
from app.modules.quiz.repository import QuizRepository
from app.modules.quiz.schemas import IncorrectItem, QuizItem, ScoreSubmitRequest, ScoreSubmitResponse


class QuizService:
    ADMARKET_CATEGORY = "ADmarket"
    ADMARKET_CATEGORY_ALIASES = {"ADmarket", "Corp", "Bidding", "Message"}
    OVERALL_CATEGORY = "전체"
    QUIZ_COUNT_PER_GAME = 10

    def __init__(self, repo: QuizRepository):
        """생성자"""
        self.repo = repo

    async def get_quizzes(self, category: Optional[str] = None) -> list[QuizItem]:
        """카테고리별(또는 전체) 퀴즈 목록 반환"""
        normalized = self._normalize_category(category)

        if normalized is None or normalized == self.OVERALL_CATEGORY:
            # 전체 챕터는 랜덤 10문제만 출제
            rows = self.repo.fetch_quizzes(limit=self.QUIZ_COUNT_PER_GAME, random_order=True)
        elif normalized == self.ADMARKET_CATEGORY:
            rows = self.repo.fetch_quizzes(categories=sorted(self.ADMARKET_CATEGORY_ALIASES))
        else:
            rows = self.repo.fetch_quizzes(category=normalized)

        return [QuizItem.model_validate(row) for row in rows]

    async def get_categories(self) -> list[str]:
        """사용 가능한 카테고리 리스트 반환"""
        raw_categories = self.repo.fetch_categories()

        normalized_set = {self._normalize_category(c) for c in raw_categories}
        normalized_set.discard(None)

        ordered = sorted([c for c in normalized_set if c != self.ADMARKET_CATEGORY])
        if self.ADMARKET_CATEGORY in normalized_set:
            return [self.ADMARKET_CATEGORY, *ordered]
        return ordered

    async def submit_score(
        self,
        user_id: str,
        score_data: ScoreSubmitRequest,
    ) -> ScoreSubmitResponse:
        """사용자 점수를 계산하여 저장하고 결과 메시지를 반환합니다."""
        category = self._normalize_category(score_data.category) or self.OVERALL_CATEGORY
        correct_count = score_data.correct
        total_questions = score_data.total
        incorrect_items: list[IncorrectItem] = []

        if score_data.user_answers:
            correct_count, total_questions, incorrect_items = self._evaluate_submitted_answers(
                score_data.user_answers,
            )

        score_percentage = (correct_count / total_questions) * 100 if total_questions else 0.0

        result = self.repo.upsert_score(user_id, category, score_percentage)
        message = "기존 점수 업데이트 성공" if result == "update" else "새 점수 저장 성공"
        return ScoreSubmitResponse(
            message=message,
            score=score_percentage,
            correct=correct_count,
            total=total_questions,
            incorrect_items=incorrect_items,
        )

    @classmethod
    def _normalize_category(cls, category: Optional[str]) -> Optional[str]:
        if category is None:
            return None

        normalized = category.strip()
        if not normalized:
            return None

        if normalized in cls.ADMARKET_CATEGORY_ALIASES:
            return cls.ADMARKET_CATEGORY

        return normalized

    def _evaluate_submitted_answers(
        self,
        user_answers: dict[str, str],
    ) -> tuple[int, int, list[IncorrectItem]]:
        quiz_map = self.repo.fetch_quizzes_by_ids(list(user_answers.keys()))

        correct_count = 0
        total_questions = 0
        incorrect_items: list[IncorrectItem] = []

        for quiz_id, submitted_answer in user_answers.items():
            quiz = quiz_map.get(quiz_id)
            if not quiz:
                continue

            total_questions += 1
            answer_text = submitted_answer or ""
            expected_answer = str(quiz["answer"])

            if is_answer_accepted(answer_text, expected_answer):
                correct_count += 1
            else:
                incorrect_items.append(
                    IncorrectItem(
                        quiz_id=quiz_id,
                        question=str(quiz["question"]),
                        user_answer=answer_text if answer_text else "(미입력)",
                        correct_answer=expected_answer,
                    ),
                )

        return correct_count, total_questions, incorrect_items

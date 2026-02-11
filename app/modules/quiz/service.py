from typing import Optional

from app.modules.quiz.repository import QuizRepository
from app.modules.quiz.schemas import QuizItem, ScoreSubmitRequest, ScoreSubmitResponse

"""
QuizService
-----------
퀴즈 관련 비즈니스 로직을 담당하는 서비스 계층입니다.

설계 주의사항:
- 서비스는 레포지토리를 호출하여 원시 데이터를 얻고,
  도메인 로직(점수 계산, 메시지 생성 등)을 수행합니다.
- 현재 레포지토리에서 커밋을 수행하므로, 서비스는 단일 호출
  단위로 동작합니다. 필요시 트랜잭션 경계를 서비스로
  이동하세요.
"""


class QuizService:
    def __init__(self, repo: QuizRepository):
        """생성자

        Args:
            repo (QuizRepository): 데이터 접근 레포지토리
        """
        self.repo = repo

    async def get_quizzes(self, category: Optional[str] = None) -> list[QuizItem]:
        """카테고리별(또는 전체) 퀴즈 목록 반환

        Args:
            category (Optional[str]): 필터할 카테고리

        Returns:
            list[QuizItem]: 검증된 퀴즈 모델 리스트
        """
        # 동기 레포지토리 호출이므로 블로킹 가능성을 감안하세요.
        rows = self.repo.fetch_quizzes(category)
        return [QuizItem.model_validate(row) for row in rows]

    async def get_categories(self) -> list[str]:
        """사용 가능한 카테고리 리스트 반환"""
        return self.repo.fetch_categories()

    async def submit_score(
        self,
        user_id: str,
        score_data: ScoreSubmitRequest,
    ) -> ScoreSubmitResponse:
        """사용자 점수를 계산하여 저장하고 결과 메시지를 반환합니다.

        Args:
            user_id (str): 점수를 저장할 사용자 ID
            score_data (ScoreSubmitRequest): 입력 데이터

        Returns:
            ScoreSubmitResponse: 저장 결과 메시지와 점수
        """
        category = score_data.category or "전체"
        correct_count = score_data.correct
        total_questions = score_data.total
        score_percentage = (correct_count / total_questions) * 100 if total_questions else 0.0

        result = self.repo.upsert_score(user_id, category, score_percentage)
        message = "기존 점수 업데이트 성공" if result == "update" else "새 점수 저장 성공"
        return ScoreSubmitResponse(message=message, score=score_percentage)

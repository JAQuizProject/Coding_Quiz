from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Quiz, Score

"""
QuizRepository
----------------
퀴즈 관련 데이터베이스 접근을 책임지는 레포지토리 계층입니다.
이 모듈은 SQLAlchemy 세션(`Session`)을 직접 사용하여 데이터 조회/수정 작업을 수행합니다.

주요 책임:
- 퀴즈 목록 조회
- 카테고리 목록 조회
- 사용자 점수 저장(업서트)

설계 주의사항:
- 이 레포지토리는 낮은 수준의 DB 작업(쿼리 실행)을 담당합니다.
  비즈니스 로직(점수 계산, 결과 메시지 등)은 서비스 계층에서
  처리하는 것을 권장합니다.
- 현재 `upsert_score`는 내부에서 `commit()`을 호출합니다.
  복수의 DB 작업을 하나의 트랜잭션으로 묶어야 하는 경우
  (서비스 레이어에서 관리)에는 commit 위치를 서비스로 옮기는
  것이 좋습니다.
"""


class QuizRepository:
    def __init__(self, db: Session):
        """생성자

        Args:
            db (Session): SQLAlchemy 세션 인스턴스 (요청 범위 DI로 주입됨)
        """
        self.db = db

    def fetch_quizzes(
        self,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """퀴즈 목록을 조회합니다.

        Args:
            category (Optional[str]): 카테고리 필터. None이면 전체 퀴즈를
                반환합니다.

        Returns:
            List[Dict[str, Any]]: 각 퀴즈를 딕셔너리 형태로 담은 리스트.
                키: id, question, explanation, answer
        """
        stmt = select(
            Quiz.id.label("id"),
            Quiz.question.label("question"),
            Quiz.explanation.label("explanation"),
            Quiz.answer.label("answer"),
        )

        if category:
            stmt = stmt.where(Quiz.category == category)

        rows = self.db.execute(stmt).mappings().all()
        return [dict(r) for r in rows]

    def fetch_categories(self) -> List[str]:
        """퀴즈 테이블에서 사용 가능한 카테고리 목록을 조회합니다.

        Returns:
            List[str]: 중복 제거된 카테고리 문자열 목록. NULL/빈 값은
                제외됩니다.
        """
        stmt = select(Quiz.category).distinct().where(Quiz.category.isnot(None), Quiz.category != "")
        categories = self.db.execute(stmt).scalars().all()
        return list(categories)

    def upsert_score(
        self,
        user_id: int,
        category: str,
        score_percentage: float,
    ):
        """사용자 점수를 삽입하거나(INSERT), 기존 점수가 있으면 업데이트(UPDATE)합니다.

        동작 설명:
        - 먼저 `Score` 모델에서 `user_id`와 `category`로 기존 레코드를 조회합니다.
        - 레코드가 존재하면 `score` 값을 업데이트하고 `commit()`을 호출합니다.
        - 존재하지 않으면 새로운 `Score` 객체를 생성하여 추가한 뒤 `commit()`을 호출합니다.

        주의:
        - 이 메서드는 내부에서 `commit()`을 수행합니다. 여러 DB 조작을
          하나의 트랜잭션으로 묶어야 할 경우(예: 여러 레포지토리 호출)
          서비스 레이어에서 트랜잭션을 관리하도록 변경하는 것이
          안전합니다.

        Args:
            user_id (int): 점수를 저장할 사용자 ID
            category (str): 점수의 카테고리
            score_percentage (float): 퍼센트 형태의 점수 (예: 80.0)

        Returns:
            str: 'update' 또는 'insert'를 반환하여 호출자에게 동작 종류를 알립니다.
        """
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

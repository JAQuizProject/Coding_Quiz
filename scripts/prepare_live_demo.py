from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import or_

from app.core.csv_listener import store_csv_to_db
from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.models import Quiz, Score, User


ROOT_DIR = Path(__file__).resolve().parent.parent
DEMO_CATEGORY = "LiveDemo"
DEMO_EMAIL = "live-demo@example.com"
DEMO_PASSWORD = "Demo1234!"
DEMO_USERNAME = "live-demo"


@dataclass(frozen=True)
class DemoQuiz:
    id: str
    question: str
    explanation: str
    answer: str


DEMO_QUIZZES = (
    DemoQuiz(
        id="01KXCNS1CZN697JRQ18CP0CT6X",
        question="[DEMO 1] 숫자 10을 소수 둘째 자리까지 입력하세요.",
        explanation="순수 숫자 표현은 값이 같으면 같은 답으로 판정해야 합니다.",
        answer="10",
    ),
    DemoQuiz(
        id="01KXCNS1CZ2RFNNX4HP2E1Q4W3",
        question="[DEMO 2] 정답 문자열 python3을 그대로 입력하세요.",
        explanation="숫자가 같아도 앞의 텍스트가 다르면 다른 답입니다.",
        answer="python3",
    ),
    DemoQuiz(
        id="01KXCNS1CZ64RG3SVW68WFY8W9",
        question="[DEMO 3] 정답 문자열 order 404를 그대로 입력하세요.",
        explanation="문자열에 포함된 숫자만 같다고 정답으로 처리하면 안 됩니다.",
        answer="order 404",
    ),
)


def prepare_demo() -> None:
    init_db()
    store_csv_to_db(str(ROOT_DIR / "csv_files" / "quiz_data.csv"))

    with SessionLocal() as session:
        user = (
            session.query(User)
            .filter(or_(User.email == DEMO_EMAIL, User.username == DEMO_USERNAME))
            .first()
        )
        if user is None:
            user = User(username=DEMO_USERNAME, email=DEMO_EMAIL, hashed_password="")
            session.add(user)

        user.username = DEMO_USERNAME
        user.email = DEMO_EMAIL
        user.hashed_password = get_password_hash(DEMO_PASSWORD)
        session.flush()

        session.query(Score).filter(
            Score.user_id == user.id,
            Score.category == DEMO_CATEGORY,
        ).delete(synchronize_session=False)

        for item in DEMO_QUIZZES:
            session.merge(
                Quiz(
                    id=item.id,
                    question=item.question,
                    explanation=item.explanation,
                    answer=item.answer,
                    category=DEMO_CATEGORY,
                )
            )

        session.commit()

    print("Live demo data is ready.")
    print(f"Login: {DEMO_EMAIL} / {DEMO_PASSWORD}")
    print(f"Category: {DEMO_CATEGORY}")


if __name__ == "__main__":
    prepare_demo()

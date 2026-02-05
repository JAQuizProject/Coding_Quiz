# ...existing code...
from sqlalchemy.orm import Session

"""
UserRepository
----------------
사용자 관련 데이터베이스 접근을 담당하는 레포지토리 계층입니다.

주요 책임:
- 이메일/사용자명으로 사용자 조회
- 사용자 생성

설계 주의사항:
- DB 작업은 동기 SQLAlchemy 세션을 사용합니다. 서비스 계층에서 트랜잭션 경계를 관리하는 것을 권장합니다.
"""


class UserRepository:
    def __init__(self, db: Session):
        """생성자

        Args:
            db (Session): SQLAlchemy 세션
        """
        self.db = db

    def get_by_email(self, email: str):
        """이메일로 사용자 조회

        Args:
            email (str): 조회할 이메일 (일반적으로 소문자 변환 후 사용)

        Returns:
            User | None: 조회된 User 객체 또는 None
        """
        from app.models.user import User

        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str):
        """사용자명으로 사용자 조회

        Args:
            username (str): 사용자명

        Returns:
            User | None: 조회된 User 객체 또는 None
        """
        from app.models.user import User

        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, username: str, email: str, hashed_password: str):
        """새로운 사용자 생성 및 DB 저장

        Args:
            username (str): 사용자명
            email (str): 이메일 (이미 소문자화되어 전달되는 것이 권장)
            hashed_password (str): bcrypt 등으로 해시된 비밀번호

        Returns:
            User: 생성된 User 객체 (커밋 및 리프레시 이후 반환)
        """
        from app.models.user import User

        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

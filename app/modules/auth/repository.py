from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    def __init__(self, db: Session):
        """생성자"""
        self.db = db

    def get_by_email(self, email: str):
        """이메일로 사용자 조회"""
        stmt = select(User).where(User.email == email)
        return self.db.scalars(stmt).first()

    def get_by_username(self, username: str):
        """사용자명으로 사용자 조회"""
        stmt = select(User).where(User.username == username)
        return self.db.scalars(stmt).first()

    def create_user(self, username: str, email: str, hashed_password: str):
        """새로운 사용자 생성 및 DB 저장"""
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

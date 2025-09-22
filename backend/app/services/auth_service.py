from datetime import timedelta
from typing import Any

from ..core.security import create_access_token, get_password_hash, verify_password
from ..repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository, token_expire_minutes: int = 30):
        self.user_repo = user_repo
        self.token_expire_minutes = token_expire_minutes

    async def signup(self, username: str, email: str, password: str) -> Any:
        email_lower = email.lower()
        if self.user_repo.get_by_email(email_lower):
            return None, "이미 존재하는 이메일입니다."

        if self.user_repo.get_by_username(username):
            return None, "이미 존재하는 사용자 이름입니다."

        hashed_password = get_password_hash(password)
        user = self.user_repo.create_user(username, email_lower, hashed_password)
        return user, None

    async def login(self, email: str, password: str):
        email_lower = email.lower()
        user = self.user_repo.get_by_email(email_lower)
        if not user:
            return None, "이메일 또는 비밀번호가 잘못되었습니다."

        if not verify_password(password, user.hashed_password):
            return None, "이메일 또는 비밀번호가 잘못되었습니다."

        access_token_expires = timedelta(minutes=self.token_expire_minutes)
        token = create_access_token(
            user_id=user.id, email=user.email, expires_delta=access_token_expires
        )
        return {
            "access_token": token,
            "user": {"id": user.id, "username": user.username},
        }, None

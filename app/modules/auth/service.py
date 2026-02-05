from datetime import timedelta
from typing import Any

from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.modules.auth.repository import UserRepository

"""
AuthService
-----------
인증 관련 비즈니스 로직을 담당하는 서비스 계층입니다.

주요 책임:
- 회원가입(중복 검사, 비밀번호 해싱, 사용자 생성)
- 로그인(이메일/비밀번호 검증, JWT 토큰 발행)

반환 규약:
- (성공값, None) 또는 (None, 오류메시지) 형태를 사용하여 라우터에서 적절한 HTTP 응답을 구성합니다.
"""


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        token_expire_minutes: int = 30,
    ):
        self.user_repo = user_repo
        self.token_expire_minutes = token_expire_minutes

    async def signup(self, username: str, email: str, password: str) -> Any:
        """회원가입 처리

        Args:
            username (str): 사용자명
            email (str): 이메일
            password (str): 평문 비밀번호

        Returns:
            Tuple(User|None, str|None): (생성된 사용자 또는 None, 오류 메시지 또는 None)
        """
        email_lower = email.lower()
        if self.user_repo.get_by_email(email_lower):
            return None, "이미 존재하는 이메일입니다."

        if self.user_repo.get_by_username(username):
            return None, "이미 존재하는 사용자 이름입니다."

        hashed_password = get_password_hash(password)
        user = self.user_repo.create_user(
            username,
            email_lower,
            hashed_password,
        )
        return user, None

    async def login(self, email: str, password: str):
        """로그인 처리 및 JWT 토큰 발행"""
        email_lower = email.lower()
        user = self.user_repo.get_by_email(email_lower)
        if not user:
            return None, "이메일 또는 비밀번호가 잘못되었습니다."

        if not verify_password(password, user.hashed_password):
            return None, "이메일 또는 비밀번호가 잘못되었습니다."

        access_token_expires = timedelta(minutes=self.token_expire_minutes)
        token = create_access_token(
            user_id=user.id,
            email=user.email,
            expires_delta=access_token_expires,
        )
        return {
            "access_token": token,
            "user": {
                "id": user.id,
                "username": user.username,
            },
        }, None

from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from pydantic import ValidationError

from .config import config
from .schemas import APIModel

# JWT 설정
SECRET_KEY = config.SECRET_KEY
ALGORITHM = "HS256"
# 토큰 유효 시간 (30분)
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES


class TokenPayload(APIModel):
    id: str
    email: str


def get_password_hash(password: str) -> str:
    """비밀번호를 해싱하여 반환"""
    password_bytes = password.encode("utf-8")

    # bcrypt backend enforces a 72-byte limit (bytes, not characters).
    if len(password_bytes) > 72:
        raise ValueError("bcrypt passwords are limited to 72 bytes")

    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """입력한 비밀번호가 해시된 비밀번호와 일치하는지 확인"""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        # Invalid hash format, etc.
        return False


def create_access_token(
    user_id: str,
    email: str,
    expires_delta: timedelta | None = None,
):
    to_encode = {"sub": email, "id": user_id}
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    print(f"JWT 생성 - Payload: {to_encode}")  # 디버깅 로그 추가

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if not isinstance(payload, dict):
            print("JWT Payload가 딕셔너리 타입이 아님")
            return None

        if "sub" not in payload or "id" not in payload:
            print(f"JWT에 'sub' 또는 'id' 키 없음, Payload: {payload}")
            return None

        try:
            return TokenPayload(
                id=payload.get("id"),
                email=payload.get("sub"),
            )
        except ValidationError:
            print(f"JWT 타입이 올바르지 않음, Payload: {payload}")
            return None

    except jwt.ExpiredSignatureError:
        print("토큰이 만료되었습니다.")
        return None
    except jwt.InvalidTokenError:
        print("유효하지 않은 토큰입니다.")
        return None

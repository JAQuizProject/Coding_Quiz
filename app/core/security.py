import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from dotenv import load_dotenv
from passlib.context import CryptContext

# 환경 변수 로드
load_dotenv()

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
# 기본값 설정
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
# 토큰 유효 시간 (30분)
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_password_hash(password: str) -> str:
    """비밀번호를 해싱하여 반환"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """입력한 비밀번호가 해시된 비밀번호와 일치하는지 확인"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, email: str, expires_delta: timedelta = None):
    to_encode = {"sub": email, "id": user_id}
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    print(f"JWT 생성 - Payload: {to_encode}")  # 디버깅 로그 추가

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if not isinstance(payload, dict):
            print("❌ JWT Payload가 딕셔너리 타입이 아님")
            return None

        if "sub" not in payload or "id" not in payload:
            print(f"❌ JWT에 'sub' 또는 'id' 키 없음, Payload: {payload}")
            return None

        return {"id": payload["id"], "email": payload["sub"]}

    except jwt.ExpiredSignatureError:
        print("❌ 토큰이 만료되었습니다.")
        return None
    except jwt.InvalidTokenError:
        print("❌ 유효하지 않은 토큰입니다.")
        return None

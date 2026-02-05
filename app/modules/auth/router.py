import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.modules.auth.repository import UserRepository
from app.modules.auth.schemas import UserCreate, UserLogin
from app.modules.auth.service import AuthService

router = APIRouter()

# OAuth2PasswordBearer는 FastAPI에서 JWT 기반 인증을 위해 사용됨
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# JWT 만료 시간 설정 (환경 변수에서 가져오기)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


def _get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    repo = UserRepository(db)
    return AuthService(repo, token_expire_minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


@router.post("/signup")
async def signup(user: UserCreate, auth_service: AuthService = Depends(_get_auth_service)):
    new_user, err = await auth_service.signup(
        user.username,
        user.email,
        user.password,
    )
    if err:
        raise HTTPException(status_code=400, detail=err)

    return {
        "message": "회원가입 성공!",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
        },
    }


@router.post("/login")
async def login(user: UserLogin, auth_service: AuthService = Depends(_get_auth_service)):
    result, err = await auth_service.login(user.email, user.password)
    if err:
        raise HTTPException(status_code=401, detail=err)

    return {"message": "로그인 성공!", **result}


@router.post("/verify-token")
async def verify_token(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload or "id" not in payload or "email" not in payload:
        raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 토큰입니다.")

    return {"message": "토큰이 유효합니다.", "user": payload["email"]}


@router.post("/logout")
async def logout():
    return {"message": "로그아웃 성공! 클라이언트에서 토큰을 삭제하세요."}

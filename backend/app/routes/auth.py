import os
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.user import User
from ..core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from pydantic import BaseModel
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()

# OAuth2PasswordBearer는 FastAPI에서 JWT 기반 인증을 위해 사용됨
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# JWT 만료 시간 설정 (환경 변수에서 가져오기)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# 회원가입 요청 모델
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# 로그인 요청 모델
class UserLogin(BaseModel):
    email: str
    password: str

# 회원가입 API
@router.post("/signup")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    # 이메일을 소문자로 변환
    email_lower = user.email.lower()
    existing_email = db.query(User).filter(User.email == email_lower).first()

    if existing_email:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자 이름입니다.")

    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, email=email_lower, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "회원가입 성공!",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
    }



@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):

    # 이메일을 소문자로 변환
    email_lower = user.email.lower()
    db_user = db.query(User).filter(User.email == email_lower).first()

    # 1. DB에서 유저가 조회되는지 확인
    if not db_user:
        print(f"[DEBUG] 유저를 찾을 수 없음: {user.email}")
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다.")

    print(f" [DEBUG] 유저 찾음: {db_user.username}")
    print(f" [DEBUG] 저장된 해시된 비밀번호: {db_user.hashed_password}")

    # 2. 비밀번호 검증 과정 로그 추가
    is_password_valid = verify_password(user.password, db_user.hashed_password)
    print(f" [DEBUG] 비밀번호 검증 결과: {is_password_valid}")

    if not is_password_valid:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다.")

    # 3. JWT 토큰 생성 과정 로그 추가
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user_id=db_user.id, email=db_user.email, expires_delta=access_token_expires)

    print(f" [DEBUG] 생성된 JWT 토큰: {access_token}")

    return {
        "message": "로그인 성공!",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": db_user.id, "username": db_user.username}
    }

@router.post("/verify-token")
async def verify_token(token: str = Depends(oauth2_scheme)):
    print(f"[DEBUG] 받은 토큰: {token}")

    payload = decode_access_token(token)

    if not payload or "id" not in payload or "email" not in payload:
        print(f"[DEBUG] 토큰 검증 실패 - payload: {payload}")
        raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 토큰입니다.")

    print(f"[DEBUG] 토큰 해독 완료: {payload}")

    return {"message": "토큰이 유효합니다.", "user": payload["email"]}


# 로그아웃 API (클라이언트에서 토큰 삭제)
@router.post("/logout")
async def logout():
    return {"message": "로그아웃 성공! 클라이언트에서 토큰을 삭제하세요."}

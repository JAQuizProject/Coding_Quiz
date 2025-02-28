from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.user import User
from ..core.security import get_password_hash, verify_password
from pydantic import BaseModel

# FastAPI의 APIRouter 객체 생성
router = APIRouter()

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
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    hashed_password = get_password_hash(user.password)  # 비밀번호 해싱
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)

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

# 로그인 API
@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다.")

    return {"message": "로그인 성공!", "user": {"id": db_user.id, "username": db_user.username}}

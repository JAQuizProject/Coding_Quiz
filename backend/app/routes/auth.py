from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app.models.users import User
from pydantic import BaseModel

# FastAPI의 APIRouter 객체 생성
router = APIRouter()

# DB 세션 종속성 관리
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 회원가입 요청 모델 (DTO 역할)
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# 회원가입 엔드포인트
@router.post("/signup")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    # 📌 이메일 중복 확인
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    # 📌 새 유저 생성
    new_user = User(username=user.username, email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "회원가입 성공!", "user": {"id": new_user.id, "username": new_user.username, "email": new_user.email}}

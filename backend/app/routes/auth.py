from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import User
from pydantic import BaseModel # 요청 데이터 검증을 위한 Pydantic 모델

# FastAPI의 APIRouter 객체 생성
router = APIRouter()

# DB 세션 종속성 관리
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    print("회원가입 API 호출됨")  # 확인용 로그

    try:
        # 이메일 중복 확인
        existing_user = db.query(User).filter(User.email == user.email).first()
        print(f"기존 회원 여부 확인: {existing_user}")

        if existing_user:
            print("이미 존재하는 이메일입니다.")
            raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

        # 새 유저 생성
        new_user = User(username=user.username, email=user.email, password=user.password)
        print(f"새 유저 생성: {new_user}")

        # 데이터베이스 추가 및 커밋
        db.add(new_user)
        print("DB에 추가함")
        db.commit()
        print("DB에 저장 완료")

        # 변경 사항 반영
        db.refresh(new_user)
        print("새 유저 데이터 갱신 완료")

        return {
            "message": "회원가입 성공!",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email
            }
        }
    except Exception as e:
        print("회원가입 중 오류 발생:", str(e))
        raise HTTPException(status_code=500, detail="서버 내부 오류 발생")


# 로그인 API
@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or db_user.password != user.password:  # 해싱 없이 비밀번호 비교
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다.")

    return {"message": "로그인 성공!", "user": {"id": db_user.id, "username": db_user.username}}
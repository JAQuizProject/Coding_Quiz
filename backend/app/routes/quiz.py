from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import decode_access_token  # JWT 검증 함수 import
from sqlalchemy.sql import text

router = APIRouter()
security = HTTPBearer()  # JWT 인증을 위한 Security 객체 생성

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    JWT 토큰을 검증하고, 사용자 정보를 반환하는 함수
    """
    token = credentials.credentials  # Bearer 토큰 추출
    user = decode_access_token(token)  # ✅ 기존의 `decode_access_token()`을 사용하여 검증

    if not user:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    return user  # 검증된 사용자 정보 반환

# 퀴즈 데이터 가져오기 API (JWT 인증 필요)
@router.get("/quiz")
def get_quiz_data(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    JWT 토큰을 검증한 후, 데이터베이스에서 퀴즈 목록을 가져옴.
    """
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다.")

    try:
        quizzes = db.execute(text("SELECT id, question, explanation, answer FROM quizzes")).fetchall()
        quiz_list = [{"id": q[0], "question": q[1], "explanation": q[2], "answer": q[3]} for q in quizzes]

        return {"message": "퀴즈 데이터 조회 성공", "data": quiz_list}

    except Exception as e:
        print(f"❌ 데이터베이스 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import decode_access_token  # JWT 검증 함수 import
from sqlalchemy.sql import text
from ..models.score import Score
from ..models.user import User

router = APIRouter()
security = HTTPBearer()  # JWT 인증을 위한 Security 객체 생성

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)) -> User:
    """
    JWT 토큰을 검증하고, User 객체를 반환
    """
    token = credentials.credentials  # Bearer 토큰 추출
    user_data = decode_access_token(token)  # JWT 해독

    if not user_data or "id" not in user_data:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    # User 객체 조회
    user = db.query(User).filter(User.id == user_data["id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    return user  # User 객체 반환

# 퀴즈 데이터 가져오기 API (JWT 인증 필요)
@router.get("/get")
def get_quiz_data(category: str = None, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    JWT 토큰을 검증한 후, 특정 카테고리의 퀴즈 목록을 가져옴.
    """
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다.")

    try:
        if category:  # 특정 카테고리의 퀴즈만 가져오기
            query = text("SELECT id, question, explanation, answer FROM quizzes WHERE category = :category")
            params = {"category": category}
        else:  # 모든 퀴즈 가져오기
            query = text("SELECT id, question, explanation, answer FROM quizzes")
            params = {}

        quizzes = db.execute(query, params).fetchall()
        quiz_list = [{"id": q[0], "question": q[1], "explanation": q[2], "answer": q[3]} for q in quizzes]

        return {"message": "퀴즈 데이터 조회 성공", "data": quiz_list}

    except Exception as e:
        print(f"❌ 데이터베이스 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")

# 카테고리 목록을 가져오는 API
@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """
    데이터베이스에서 사용 가능한 카테고리 목록을 가져옴.
    """
    try:
        categories = db.execute(text("SELECT DISTINCT category FROM quizzes")).fetchall()
        category_list = [c[0] for c in categories if c[0]]  # None 값 제외
        return {"message": "카테고리 조회 성공", "data": category_list}

    except Exception as e:
        print(f"❌ 카테고리 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"카테고리 조회 오류: {str(e)}")

# 새로운 API: 퀴즈 점수 저장 (JWT 인증 필요)
@router.post("/submit")
def submit_quiz_score(score_data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    사용자의 퀴즈 점수를 데이터베이스에 저장
    """
    print("🔹 사용자 정보:", user.id, user.username)  # 디버깅용 로그 추가

    try:
        correct_count = score_data.get("correct", 0)
        total_questions = score_data.get("total", 10)

        score_percentage = (correct_count / total_questions) * 100

        new_score = Score(user_id=user.id, score=int(score_percentage))  # user.id 사용
        db.add(new_score)
        db.commit()

        return {"message": "점수 저장 성공", "score": score_percentage}

    except Exception as e:
        print(f"❌ 점수 저장 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"점수 저장 오류: {str(e)}")
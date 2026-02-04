from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.modules.quiz.repository import QuizRepository
from app.modules.quiz.schemas import ScoreSubmit
from app.modules.quiz.service import QuizService

router = APIRouter()
security = HTTPBearer()  # JWT 인증을 위한 Security 객체 생성


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
) -> User:
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


def _get_quiz_service(db: Session = Depends(get_db)) -> QuizService:
    repo = QuizRepository(db)
    return QuizService(repo)


@router.get("/get")
async def get_quiz_data(
    category: str = None,
    user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(_get_quiz_service),
):
    """
    JWT 토큰을 검증한 후, 특정 카테고리의 퀴즈 목록을 가져옴.
    """
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다.")

    try:
        quiz_list = await quiz_service.get_quizzes(category)
        return {"message": "퀴즈 데이터 조회 성공", "data": quiz_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")


@router.get("/categories")
async def get_categories(quiz_service: QuizService = Depends(_get_quiz_service)):
    """
    데이터베이스에서 사용 가능한 카테고리 목록을 가져옴.
    """
    try:
        category_list = await quiz_service.get_categories()
        return {"message": "카테고리 조회 성공", "data": category_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"카테고리 조회 오류: {str(e)}")


@router.post("/submit")
async def submit_quiz_score(
    score_data: ScoreSubmit,
    user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(_get_quiz_service),
):
    """
    사용자의 퀴즈 점수를 덮어씌우며 저장 (같은 user_id + category가 존재하면 UPDATE)
    """
    try:
        result = await quiz_service.submit_score(user.id, score_data.model_dump())
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"점수 저장 오류: {str(e)}")

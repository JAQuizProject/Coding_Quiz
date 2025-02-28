import os
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리 찾기
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# .env 파일 로드
load_dotenv(ENV_PATH)

class Config:
    """환경 변수를 관리하는 설정 클래스"""
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", 8000))

    # SQLite 경로 절대 경로로 변경하여 중복 방지
    DATABASE_PATH = BASE_DIR / "quiz_app.db"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "mysecretkey")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

config = Config()

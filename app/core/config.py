import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

# 프로젝트 루트 디렉토리 찾기
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# .env 파일 로드
load_dotenv(ENV_PATH)


class Config(BaseModel):
    """환경 변수를 관리하는 설정 모델."""

    model_config = ConfigDict(extra="forbid")

    BACKEND_HOST: str = Field(default="0.0.0.0")
    BACKEND_PORT: int = Field(default=8000)
    DATABASE_PATH: Path
    DATABASE_URL_DEV: str
    DATABASE_URL_PROD: str | None = Field(default=None)
    ENV: str = Field(default="development")
    DATABASE_URL: str
    SECRET_KEY: str = Field(default="mysecretkey")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)


def load_config() -> Config:
    """환경 변수를 읽어 Config 인스턴스를 생성합니다."""
    database_path = BASE_DIR / "quiz_app.db"
    env = os.getenv("ENV", "development")
    database_url_dev = os.getenv("DATABASE_URL_DEV", f"sqlite:///{database_path}")
    database_url_prod = os.getenv("DATABASE_URL")
    database_url = database_url_prod if env == "production" and database_url_prod else database_url_dev

    return Config(
        BACKEND_HOST=os.getenv("BACKEND_HOST", "0.0.0.0"),
        BACKEND_PORT=os.getenv("BACKEND_PORT", 8000),
        DATABASE_PATH=database_path,
        DATABASE_URL_DEV=database_url_dev,
        DATABASE_URL_PROD=database_url_prod,
        ENV=env,
        DATABASE_URL=database_url,
        SECRET_KEY=os.getenv("SECRET_KEY", "mysecretkey"),
        ACCESS_TOKEN_EXPIRE_MINUTES=os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30),
    )


config = load_config()
print(f"ENV 설정값: {config.ENV}")
print(f"사용할 DATABASE_URL: {config.DATABASE_URL}")

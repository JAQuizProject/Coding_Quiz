import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

# 프로젝트 루트 디렉토리 찾기
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# .env 파일 로드
load_dotenv(ENV_PATH)


def _parse_bool(raw_value: str | None, default: bool) -> bool:
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _parse_origins(raw_value: str | None, default: list[str]) -> list[str]:
    if not raw_value:
        return default

    origins = [origin.strip().rstrip("/") for origin in raw_value.split(",") if origin.strip()]
    return origins or default


class Config(BaseModel):
    """환경 변수를 관리하는 설정 모델."""

    model_config = ConfigDict(extra="forbid")

    BACKEND_HOST: str = Field(default="0.0.0.0")
    BACKEND_PORT: int = Field(default=8000)
    DATABASE_PATH: Path
    DATABASE_URL_DEV: str
    DATABASE_URL_PROD: str | None = Field(default=None)
    ENV: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    DATABASE_URL: str
    SECRET_KEY: str = Field(default="mysecretkey")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    CORS_ALLOWED_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    FCM_TEST_PROXY_ENABLED: bool = Field(default=True)
    TVCF_NOTIFICATION_BASE_URL: str = Field(default="http://127.0.0.1:8001")
    TVCF_NOTIFICATION_DEVICE_PATH: str = Field(default="/v1/devices")
    TVCF_NOTIFICATION_SUBSCRIPTION_PATH: str = Field(default="/v1/subscriptions")
    TVCF_NOTIFICATION_SEND_USER_PATH: str = Field(default="/v1/messages:sendUser")
    TVCF_NOTIFICATION_SEND_DEFINITION_PATH: str = Field(default="/v1/messages:sendDefinition")
    TVCF_NOTIFICATION_AUTH_TOKEN: str | None = Field(default=None)
    TVCF_NOTIFICATION_USER_AGENT: str = Field(default="CodingQuiz-FCM-Test/1.0")
    TVCF_NOTIFICATION_TIMEOUT_SECONDS: int = Field(default=10)
    FCM_TEST_TEMPLATE_CODE: str | None = Field(default=None)
    FCM_TEST_DEFINITION_CODE: str | None = Field(default=None)


def load_config() -> Config:
    """환경 변수를 읽어 Config 인스턴스를 생성합니다."""
    database_path = BASE_DIR / "quiz_app.db"
    env = os.getenv("ENV", "development").lower()
    is_production = env == "production"
    database_url_dev = os.getenv("DATABASE_URL_DEV", f"sqlite:///{database_path}")
    database_url_prod = os.getenv("DATABASE_URL")
    database_url = database_url_prod if is_production and database_url_prod else database_url_dev
    debug = _parse_bool(os.getenv("DEBUG"), default=not is_production)
    default_origins = [] if is_production else ["http://localhost:3000"]
    cors_allowed_origins = _parse_origins(os.getenv("CORS_ALLOWED_ORIGINS"), default_origins)
    fcm_test_proxy_enabled = _parse_bool(os.getenv("FCM_TEST_PROXY_ENABLED"), default=not is_production)

    return Config(
        BACKEND_HOST=os.getenv("BACKEND_HOST", "0.0.0.0"),
        BACKEND_PORT=os.getenv("BACKEND_PORT", 8000),
        DATABASE_PATH=database_path,
        DATABASE_URL_DEV=database_url_dev,
        DATABASE_URL_PROD=database_url_prod,
        ENV=env,
        DEBUG=debug,
        DATABASE_URL=database_url,
        SECRET_KEY=os.getenv("SECRET_KEY", "mysecretkey"),
        ACCESS_TOKEN_EXPIRE_MINUTES=os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30),
        CORS_ALLOWED_ORIGINS=cors_allowed_origins,
        FCM_TEST_PROXY_ENABLED=fcm_test_proxy_enabled,
        TVCF_NOTIFICATION_BASE_URL=os.getenv("TVCF_NOTIFICATION_BASE_URL", "http://127.0.0.1:8001"),
        TVCF_NOTIFICATION_DEVICE_PATH=os.getenv("TVCF_NOTIFICATION_DEVICE_PATH", "/v1/devices"),
        TVCF_NOTIFICATION_SUBSCRIPTION_PATH=os.getenv("TVCF_NOTIFICATION_SUBSCRIPTION_PATH", "/v1/subscriptions"),
        TVCF_NOTIFICATION_SEND_USER_PATH=os.getenv(
            "TVCF_NOTIFICATION_SEND_USER_PATH",
            "/v1/messages:sendUser",
        ),
        TVCF_NOTIFICATION_SEND_DEFINITION_PATH=os.getenv(
            "TVCF_NOTIFICATION_SEND_DEFINITION_PATH",
            "/v1/messages:sendDefinition",
        ),
        TVCF_NOTIFICATION_AUTH_TOKEN=os.getenv("TVCF_NOTIFICATION_AUTH_TOKEN"),
        TVCF_NOTIFICATION_USER_AGENT=os.getenv("TVCF_NOTIFICATION_USER_AGENT", "CodingQuiz-FCM-Test/1.0"),
        TVCF_NOTIFICATION_TIMEOUT_SECONDS=int(os.getenv("TVCF_NOTIFICATION_TIMEOUT_SECONDS", 10)),
        FCM_TEST_TEMPLATE_CODE=os.getenv("FCM_TEST_TEMPLATE_CODE"),
        FCM_TEST_DEFINITION_CODE=os.getenv("FCM_TEST_DEFINITION_CODE"),
    )


config = load_config()
print(f"ENV 설정값: {config.ENV}")
print(f"사용할 DATABASE_URL: {config.DATABASE_URL}")

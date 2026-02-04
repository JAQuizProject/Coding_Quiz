from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from ..core.config import config

# PostgreSQL 사용 시 connect_args 필요 없음
connect_args = {}
if "sqlite" in config.DATABASE_URL:
    connect_args = {"check_same_thread": False}  # SQLite 전용 옵션

# 데이터베이스 엔진 생성
engine = create_engine(config.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 기본 모델 클래스
Base = declarative_base()

# DB 초기화 함수
def init_db():
    """데이터베이스 테이블 생성"""
    from ..models import quiz, user  # models import

    # 테이블 중복 생성 방지
    Base.metadata.create_all(bind=engine)

def get_db():
    """세션을 제공하는 함수 (FastAPI Depends 용)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import csv_listener  # CSV 감시 모듈 import
from app.core.config import config
from app.core.database import init_db
from app.core.schemas import MessageResponse
from app.modules import api_router

# 현재 실행 중인 파일의 디렉토리를 기준으로 Python path 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(debug=config.DEBUG)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB 초기화
init_db()

# 라우터 등록
app.include_router(api_router)


@app.get("/", response_model=MessageResponse)
def read_root():
    return {"message": "Welcome to the Coding Quiz API!"}


# 서버 실행 시 CSV 감시 자동 시작
# FastAPI 최신 버전에서 @app.on_event()이 비권장됨 (Deprecated)
# Linter(Pylance, MyPy 등)가 Deprecation을 감지하여 경고 표시
# FastAPI 버전과 Python 버전이 맞지 않을 가능성

# 해결 방법
# 최신 방식 (lifespan) 사용
# FastAPI 버전 업데이트
# Linter 경고 무시


@app.on_event("startup")
def on_startup():
    csv_listener.start_csv_listener()  # 서버 시작 시 감시 시작
    for route in api_router.routes:
        print(f" {route.path} -> {route.methods}")


@app.on_event("shutdown")
def on_shutdown():
    csv_listener.stop_csv_listener()  # 서버 종료 시 감시 중지

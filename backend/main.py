import sys
import os

# 현재 실행 중인 파일의 디렉토리를 기준으로 Python path 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db
from app.routes.auth import router as auth_router

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB 초기화
init_db()

# 라우터 등록
app.include_router(auth_router, prefix="/auth")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Coding Quiz API!"}

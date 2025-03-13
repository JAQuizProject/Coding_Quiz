# 베이스 이미지 설정 (Python 3.10)
FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 복사 & 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 환경변수 로드
ENV PYTHONPATH=/app \
    ENV=production \
    BACKEND_HOST=0.0.0.0 \
    BACKEND_PORT=8000 \
    DATABASE_URL=postgresql://ajh:1234@fastapi-db.c01gcokig976.us-east-1.rds.amazonaws.com/fastapi_db \
    SECRET_KEY=8d733e9c4db2e2f9f4e7d6cf3a86f8bca33c3a74e788d089a3 \
    ACCESS_TOKEN_EXPIRE_MINUTES=30

# FastAPI 실행 (Uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
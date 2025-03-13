# 베이스 이미지 설정 (Python 3.10)
FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 복사 & 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .


# FastAPI 실행 (Uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# 베이스 이미지 설정 (Python 3.13)
FROM python:3.13-slim

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 설치 및 가상환경 비활성화
ENV POETRY_VERSION=2.2.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# 의존성 설치
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-ansi --extras "postgres"

# 소스 코드 복사
COPY . .

# FastAPI 실행 (Uvicorn)
CMD ["sh", "-c", "poetry run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

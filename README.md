# Coding Quiz Project

FastAPI(백엔드) + Next.js(프론트엔드) 기반 코딩 퀴즈 플랫폼입니다.  
로그인 후 카테고리별 문제를 풀고, 점수를 저장하고, 랭킹을 확인할 수 있습니다.

## 핵심 업데이트 (현재 기준)
- `전체` 카테고리는 매번 랜덤 10문제 출제
- `ADmarket` 카테고리는 `ADmarket / Corp / Bidding / Message`를 통합해서 처리
- 퀴즈 페이지는 10문항 단위 페이지네이션
- `다시 풀기`로 로컬 진행 상태/결과 초기화 가능
- 제출 시 프론트 계산값이 아닌 **백엔드 재채점**으로 점수 저장
- 정답 판정은 허용 범위(공백/기호/대소문자/일부 오타 유사도) 기반
- 즉시 채점 UI에서 입력 답, 정답, 판정 기준, 정확도 확인 가능

---

## 기술 스택

### Backend
- Python 3.13+
- FastAPI, Uvicorn
- SQLAlchemy
- Pydantic v2
- PyJWT, passlib[bcrypt]
- Watchdog (CSV 변경 감시)
- Poetry

### Frontend
- Next.js 15
- React 19
- React-Bootstrap / Bootstrap 5
- Fetch API / Axios

---

## 주요 기능

### 인증
- 회원가입/로그인/JWT 검증
- 보호된 퀴즈 제출 API

### 퀴즈
- 카테고리별 문제 조회
- `전체`: 랜덤 10문제
- `ADmarket`: 통합 카테고리 묶음
- 10개씩 페이지네이션
- 즉시 정답 확인 + 제출 후 결과 페이지
- 서버 기준 정답 판정 및 점수 저장(카테고리별 upsert)

### 채점
- 다중 정답(`/`) 지원
- 정규화 비교(공백/기호/대소문자)
- 숫자 허용 오차(±0.01)
- 보수적 유사도 판정

### 랭킹
- 카테고리별 TOP 랭킹 조회
- `ADmarket` 통합 카테고리로 일관 표시

### 데이터 관리
- `csv_files/quiz_data.csv`를 서버 시작 시 동기화
- CSV 수정 감지 시 DB 자동 반영(merge)

---

## API 요약

### Auth
- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/verify-token`
- `POST /auth/logout`

### Quiz
- `GET /quiz/get?category=...`
- `GET /quiz/categories`
- `POST /quiz/submit`

`/quiz/submit` 요청 예시:

```json
{
  "category": "전체",
  "total": 10,
  "user_answers": {
    "01KH2YQ2VEAAW3HHBQ684D48ZE": "spring",
    "01KH2YQ2VEVWWGM0VHMJCP4YMC": "DI"
  }
}
```

### Ranking
- `GET /ranking/get?category=전체&limit=10`

---

## 로컬 실행

### 1) 백엔드
```bash
poetry install --with dev
poetry run uvicorn main:app --reload
```

PostgreSQL 사용 시:
```bash
poetry install --extras "postgres"
```

### 2) 프론트엔드
```bash
cd frontend
npm install
npm run dev
```

---

## 환경 변수

백엔드 루트 `.env` 예시:

```env
ENV=development
DEBUG=true
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DATABASE_URL_DEV=sqlite:///./quiz_app.db
# 운영에서 PostgreSQL 사용 시 설정
# DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname
SECRET_KEY=your_secret_key_change_me
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

프론트 `frontend/.env.local` 예시:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

템플릿 파일:
- `.env.example`
- `frontend/.env.example`

---

## 배포 순서 (권장: Vercel + Render)

### 1) PostgreSQL 준비
- 운영 DB를 생성하고 접속 문자열(`DATABASE_URL`) 확보

### 2) 백엔드 배포 (Render 등)
- 이 저장소의 `Dockerfile`로 배포
- 환경 변수 설정:
  - `ENV=production`
  - `DEBUG=false`
  - `DATABASE_URL=postgresql+psycopg2://...`
  - `SECRET_KEY=...`
  - `ACCESS_TOKEN_EXPIRE_MINUTES=30`
  - `CORS_ALLOWED_ORIGINS=https://<프론트도메인>`
- 프론트 도메인이 여러 개인 경우 콤마로 구분:
  - `CORS_ALLOWED_ORIGINS=https://a.example.com,https://b.example.com`

### 3) 프론트 배포 (Vercel)
- `frontend` 디렉터리를 프로젝트 루트로 지정
- 환경 변수 설정:
  - `NEXT_PUBLIC_API_URL=https://<백엔드도메인>`

### 4) 배포 확인
- `POST /auth/signup`
- `POST /auth/login`
- `GET /quiz/categories`
- `GET /ranking/get?category=전체`

---

## 현재 프로젝트 구조

```text
.
├── app
│   ├── core
│   │   ├── config.py
│   │   ├── csv_listener.py
│   │   ├── database.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   └── ulid.py
│   ├── models
│   │   ├── quiz.py
│   │   ├── score.py
│   │   └── user.py
│   └── modules
│       ├── auth
│       ├── quiz
│       │   └── grading.py
│       └── ranking
├── csv_files
│   └── quiz_data.csv
├── frontend
│   ├── api
│   ├── app
│   │   ├── login
│   │   ├── quiz
│   │   ├── ranking
│   │   ├── result
│   │   └── signup
│   ├── components
│   ├── context
│   ├── public
│   │   └── illustrations
│   └── utils
│       └── answerMatcher.js
├── main.py
├── pyproject.toml
└── README.md
```

---

## 프로젝트 미리보기 (현재 리소스 기준)

### 메인(히어로)
![메인 히어로](frontend/public/illustrations/hero-dashboard.svg)

### 메인 상세 카드
![전체 랜덤 10문제](frontend/public/illustrations/detail-random10.svg)
![ADmarket 통합](frontend/public/illustrations/detail-admarket.svg)

### 로그인/회원가입 안내 비주얼
![로그인 비주얼](frontend/public/illustrations/login-score-save.svg)
![회원가입 비주얼](frontend/public/illustrations/signup-score-track.svg)

### 기타 화면 스크린샷 리소스
![퀴즈](frontend/public/quiz.png)
![랭킹](frontend/public/ranking.png)
![결과](frontend/public/result.png)

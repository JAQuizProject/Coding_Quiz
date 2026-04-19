# Coding Quiz

FastAPI 백엔드와 Next.js 프론트엔드로 만든 코딩 퀴즈 테스트 프로젝트입니다.
로그인 후 카테고리별 문제를 풀고, 서버 채점 결과를 저장하고, 랭킹을 확인할 수 있습니다.

이 프로젝트에는 `tvcf-notification-be` 알림 서버를 검증하기 위한 foreground FCM 테스트 화면도 포함되어 있습니다.
`Coding_Quiz`가 알림 서버 역할을 하는 것은 아니고, 실제 서비스 프로젝트처럼 알림 서버에 token 등록과 발송 요청을 보내는 테스트 클라이언트 역할만 합니다.

## 문서

| 문서 | 내용 |
| --- | --- |
| [CODING_QUIZ_FCM_TEST.md](./CODING_QUIZ_FCM_TEST.md) | 로컬에서 `/fcm-test`로 알림 서버 FCM 발송을 확인하는 실행 절차 |
| [FCM_TEST_FLOW_PRESENTATION.md](./FCM_TEST_FLOW_PRESENTATION.md) | 발표/공유용 FCM 테스트 흐름 요약 |
| [FCM_CONSOLE_SETUP.md](./FCM_CONSOLE_SETUP.md) | Firebase Console에서 Web app, VAPID key, service account를 준비하는 방법 |
| [NOTIFICATION_PROJECT_INTEGRATION_GUIDE.md](./NOTIFICATION_PROJECT_INTEGRATION_GUIDE.md) | 실제 서비스 프로젝트가 notification-be에 붙을 때의 역할 분리 |
| [NOTIFICATION_BE_MEETING_NOTES.md](./NOTIFICATION_BE_MEETING_NOTES.md) | 테스트 중 확인한 notification-be 쪽 논의 안건 |
| [API_STYLE.md](./API_STYLE.md) | API 응답/요청 스타일 참고 |

읽는 순서:

```text
1. README.md
2. CODING_QUIZ_FCM_TEST.md
3. FCM_CONSOLE_SETUP.md
4. FCM_TEST_FLOW_PRESENTATION.md
5. NOTIFICATION_PROJECT_INTEGRATION_GUIDE.md
6. NOTIFICATION_BE_MEETING_NOTES.md
```

## 핵심 기능

- 회원가입, 로그인, JWT 기반 인증
- 카테고리별 퀴즈 조회
- `전체` 카테고리 랜덤 10문제 출제
- `ADmarket` 관련 카테고리 통합 처리
- 서버 재채점 기반 점수 저장
- 카테고리별 랭킹 조회
- CSV 파일 기반 퀴즈 데이터 동기화
- 알림 서버 foreground FCM 테스트 페이지

## 기술 스택

Backend:

- Python 3.13+
- FastAPI
- SQLAlchemy
- Pydantic v2
- PyJWT
- Watchdog

Frontend:

- Next.js 15
- React 19
- Bootstrap / React-Bootstrap
- Firebase Web SDK

## 로컬 실행

백엔드:

```bash
cd ~/tvcf/Coding_Quiz
source .venv/Scripts/activate
uvicorn main:app --reload --port 8000
```

프론트엔드:

```bash
cd ~/tvcf/Coding_Quiz/frontend
npm install
npm run dev
```

접속:

```text
http://localhost:3000
```

## 환경 변수

백엔드 `.env` 기본값:

```env
ENV=development
DEBUG=true
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DATABASE_URL_DEV=sqlite:///./quiz_app.db
SECRET_KEY=change-this-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

프론트 `frontend/.env.local` 기본값:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

템플릿:

- [.env.example](./.env.example)
- [frontend/.env.example](./frontend/.env.example)

## 주요 API

Auth:

- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/verify-token`
- `POST /auth/logout`

Quiz:

- `GET /quiz/get?category=...`
- `GET /quiz/categories`
- `POST /quiz/submit`

Ranking:

- `GET /ranking/get?category=전체&limit=10`

FCM test proxy:

- `GET /fcm-test/config`
- `POST /fcm-test/register-device`
- `POST /fcm-test/send`

## FCM 알림 서버 테스트 요약

목적:

```text
Coding_Quiz frontend
  -> Coding_Quiz backend
  -> tvcf-notification-be
  -> Firebase FCM
  -> 브라우저 foreground 수신
```

역할:

- `Coding_Quiz frontend`: FCM token 발급, foreground 수신 로그 표시
- `Coding_Quiz backend`: 로그인 유저 기준으로 notification-be에 token 등록/발송 요청 전달
- `tvcf-notification-be`: User, Template, Device token을 조회하고 Firebase FCM 발송

준비해야 하는 것:

| 위치 | 필요한 값 |
| --- | --- |
| Firebase Console | Web app config, VAPID key, service account JSON |
| Coding_Quiz frontend | Firebase public env, `NEXT_PUBLIC_API_URL` |
| Coding_Quiz backend | notification-be URL, template code |
| notification-be DB | `User_TM.UserId`, `NotificationTemplate_TM.Code` |
| notification-be 실행 환경 | `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_CLOUD_PROJECT` |

필요한 기준:

```text
Coding_Quiz 로그인 username
= notification-be User_TM.UserId
= NotificationDevice_TM.UserId
= /v1/messages:sendUser body.user_id
```

테스트 페이지:

```text
http://localhost:3000/fcm-test
```

테스트 순서:

```text
1. Coding_Quiz 로그인
2. FCM token 발급
3. Token 등록
4. CodingQuiz 백엔드로 발송 요청
5. Foreground 수신 로그 확인
```

화면에서 보는 성공 기준:

```text
발송 응답: target 1, success 1, failure 0
수신 로그: title/body payload 표시
```

자세한 실행 절차는 [CODING_QUIZ_FCM_TEST.md](./CODING_QUIZ_FCM_TEST.md)를 봅니다.

## 검증 명령

백엔드 테스트:

```bash
python -m pytest tests/test_notification_test_api.py -q
```

백엔드 lint:

```bash
ruff check .
```

프론트 lint/build:

```bash
cd frontend
npm run lint
npm run build
```

## 프로젝트 구조

```text
.
├── app
│   ├── core
│   ├── models
│   └── modules
│       ├── auth
│       ├── notification_test
│       ├── quiz
│       └── ranking
├── csv_files
│   └── quiz_data.csv
├── frontend
│   ├── api
│   ├── app
│   ├── components
│   ├── context
│   └── public
├── tests
├── main.py
├── pyproject.toml
└── README.md
```

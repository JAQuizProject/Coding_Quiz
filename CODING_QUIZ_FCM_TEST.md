# Coding_Quiz FCM 로컬 테스트

이 문서는 `Coding_Quiz`를 이용해 `tvcf-notification-be`의 foreground FCM 발송을 확인하는 최소 절차를 정리한다.

`Coding_Quiz`는 알림 서버가 아니다.
실제 서비스 프로젝트처럼 token 등록과 발송 요청을 알림 서버로 넘기는 테스트 클라이언트다.

## 목표

```text
Coding_Quiz frontend
  -> FCM token 발급
  -> foreground 수신 로그 표시

Coding_Quiz backend
  -> 로그인 유저 확인
  -> notification-be /v1/devices 호출
  -> notification-be /v1/messages:sendUser 호출

tvcf-notification-be
  -> DB에서 user/template/device token 조회
  -> Firebase Admin SDK로 FCM 발송
```

## 사용자 기준

현재 테스트에서 사용자 기준은 하나다.

```text
Coding_Quiz 로그인 username
= notification-be User_TM.UserId
```

따라서 notification-be DB에는 Coding_Quiz 로그인 `username`과 같은 `User_TM.UserId`가 있어야 한다.

## 필요한 준비

notification-be DB:

```text
User_TM.UserId = <Coding_Quiz 로그인 username>
NotificationTemplate_TM.Code = <테스트 template_code>
```

Coding_Quiz backend `.env`:

```env
FCM_TEST_PROXY_ENABLED=true
TVCF_NOTIFICATION_BASE_URL=http://127.0.0.1:8001
TVCF_NOTIFICATION_DEVICE_PATH=/v1/devices
TVCF_NOTIFICATION_SEND_USER_PATH=/v1/messages:sendUser
TVCF_NOTIFICATION_USER_AGENT=CodingQuiz-FCM-Test/1.0
TVCF_NOTIFICATION_TIMEOUT_SECONDS=10
FCM_TEST_TEMPLATE_CODE=<notification-be NotificationTemplate_TM.Code>
```

Coding_Quiz frontend `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_NOTIFICATION_TEST_TEMPLATE_CODE=<notification-be NotificationTemplate_TM.Code>

NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...
NEXT_PUBLIC_FIREBASE_VAPID_KEY=...
```

notification-be 실행 환경:

```env
GOOGLE_APPLICATION_CREDENTIALS=<Firebase service account JSON 경로>
GOOGLE_CLOUD_PROJECT=<Firebase project id>
```

Firebase 설정값 준비는 [FCM_CONSOLE_SETUP.md](./FCM_CONSOLE_SETUP.md)를 본다.

## 실행

notification-be:

```bash
cd ~/tvcf/tvcf-notification-be
source .venv/Scripts/activate
uvicorn app.main:app --reload --port 8001
```

Coding_Quiz backend:

```bash
cd ~/tvcf/Coding_Quiz
source .venv/Scripts/activate
uvicorn main:app --reload --port 8000
```

Coding_Quiz frontend:

```bash
cd ~/tvcf/Coding_Quiz/frontend
npm run dev
```

테스트 페이지:

```text
http://localhost:3000/fcm-test
```

## 화면 테스트 순서

```text
1. Coding_Quiz 로그인
2. /fcm-test 접속
3. FCM token 발급
4. Token 등록
5. CodingQuiz 백엔드로 발송 요청
6. Foreground 수신 로그 확인
```

성공 기준:

```text
target_count = 1
success_count = 1
failure_count = 0
Foreground 수신 로그에 title/body 표시
```

## 요청 흐름

Token 등록:

```text
frontend
  -> POST /fcm-test/register-device
  -> Authorization: Bearer <Coding_Quiz login token>

backend
  -> 로그인 유저 username 확인
  -> notification-be용 JWT { userId: username } 생성
  -> POST /v1/devices
```

발송 요청:

```text
frontend
  -> POST /fcm-test/send

backend
  -> POST /v1/messages:sendUser
  -> body: { user_id: username, template_code }
```

## 참고

이 테스트는 foreground 수신 확인용이다.
background 알림창, 모바일 push, 운영 SSO 흐름은 테스트 범위가 아니다.

테스트 중 발견한 notification-be 쪽 논의 사항은 [NOTIFICATION_BE_MEETING_NOTES.md](./NOTIFICATION_BE_MEETING_NOTES.md)에 정리한다.

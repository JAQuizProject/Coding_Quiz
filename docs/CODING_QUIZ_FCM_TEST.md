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
  -> notification-be /v1/subscriptions 호출
  -> notification-be /v1/messages:sendUser 호출
  -> notification-be /v1/messages:sendDefinition 호출

tvcf-notification-be
  -> DB에서 user/template/subscription/device token 조회
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
NotificationDefinition_TM.Code = <테스트 definition_code>
```

유저 직접 발송은 `User_TM`, `NotificationTemplate_TM`, `NotificationDevice_TM`가 필요하다.
구독 기반 발송은 `/fcm-test` 화면에서 `Definition 구독 등록`을 먼저 실행해 `NotificationSubscription_TM`에 로그인 username과 definition을 연결한다.

```text
로그인 username
  -> token 등록 대상 UserId
  -> sendUser 발송 대상 user_id
  -> NotificationDevice_TM.UserId
  -> sendDefinition 테스트에서는 NotificationSubscription_TM.UserId
```

Coding_Quiz backend `.env`:

```env
FCM_TEST_PROXY_ENABLED=true
TVCF_NOTIFICATION_BASE_URL=http://127.0.0.1:8001
TVCF_NOTIFICATION_DEVICE_PATH=/v1/devices
TVCF_NOTIFICATION_SUBSCRIPTION_PATH=/v1/subscriptions
TVCF_NOTIFICATION_SEND_USER_PATH=/v1/messages:sendUser
TVCF_NOTIFICATION_SEND_DEFINITION_PATH=/v1/messages:sendDefinition
TVCF_NOTIFICATION_USER_AGENT=CodingQuiz-FCM-Test/1.0
TVCF_NOTIFICATION_TIMEOUT_SECONDS=10
FCM_TEST_TEMPLATE_CODE=<notification-be NotificationTemplate_TM.Code>
FCM_TEST_DEFINITION_CODE=<notification-be NotificationDefinition_TM.Code>
```

Coding_Quiz frontend `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_NOTIFICATION_TEST_TEMPLATE_CODE=<notification-be NotificationTemplate_TM.Code>
NEXT_PUBLIC_NOTIFICATION_TEST_DEFINITION_CODE=<notification-be NotificationDefinition_TM.Code>

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
5. 구독 기반 발송을 테스트할 경우 Definition 구독 등록
6. 유저 직접 발송 또는 구독 기반 발송 요청
7. Foreground 수신 로그 확인
```

성공 기준:

```text
target_count = 1
success_count = 1
failure_count = 0
Foreground 수신 로그에 title/body 표시
```

화면에서 확인할 값:

| 영역 | 확인 내용 |
| --- | --- |
| 1. Token 발급 | 권한 상태가 `granted`이고 textarea에 FCM token 표시 |
| 2. Token 등록 | Base URL, Device API, Subscription API, Send User API, Send Definition API가 로컬 notification-be 주소와 일치 |
| 3. 구독 등록 | 로그인 username과 definition code로 `NotificationSubscription_TM` 연결 |
| 4. 유저 직접 발송 | 로그인 username과 template code로 `sendUser` 테스트 |
| 5. 구독 기반 발송 | definition code와 template code로 `sendDefinition` 테스트 |
| 6. Foreground 수신 로그 | 발송 후 title/body payload가 표시됨 |

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

notification-be로 전달되는 body:

```json
{
  "registration_token": "<browser fcm token>"
}
```

구독 등록:

```text
frontend
  -> POST /fcm-test/subscribe-definition

backend
  -> POST /v1/subscriptions
  -> body: { user_id: username, definition_code }
```

notification-be로 전달되는 body:

```json
{
  "user_id": "<Coding_Quiz 로그인 username>",
  "definition_code": "<NotificationDefinition_TM.Code>"
}
```

유저 직접 발송:

```text
frontend
  -> POST /fcm-test/send

backend
  -> POST /v1/messages:sendUser
  -> body: { user_id: username, template_code }
```

notification-be로 전달되는 body:

```json
{
  "user_id": "<Coding_Quiz 로그인 username>",
  "template_code": "<NotificationTemplate_TM.Code>"
}
```

구독 기반 발송:

```text
frontend
  -> POST /fcm-test/send-definition

backend
  -> POST /v1/messages:sendDefinition
  -> body: { definition_code, template_code }
```

notification-be로 전달되는 body:

```json
{
  "definition_code": "<NotificationDefinition_TM.Code>",
  "template_code": "<NotificationTemplate_TM.Code>"
}
```

이 방식은 `NotificationSubscription_TM`에서 해당 definition을 구독한 유저들의 active device token을 찾아 발송한다.

응답에서 보는 값:

```text
target_count:
  notification-be가 찾은 발송 대상 token 수

success_count:
  Firebase가 성공 처리한 token 수

failure_count:
  Firebase 발송 실패 token 수
```

## 참고

이 테스트는 foreground 수신 확인용이다.
background 알림창, 모바일 push, 운영 SSO 흐름은 테스트 범위가 아니다.

테스트 중 발견한 notification-be 쪽 논의 사항은 [NOTIFICATION_BE_MEETING_NOTES.md](./NOTIFICATION_BE_MEETING_NOTES.md)에 정리한다.

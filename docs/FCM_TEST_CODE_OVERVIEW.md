# FCM 테스트 코드 구성

이 문서는 `Coding_Quiz`에 추가된 FCM 테스트 코드 위치와 역할만 정리한다.

## 핵심 원칙

`Coding_Quiz`는 FCM을 직접 발송하지 않는다.

```text
frontend
  -> Coding_Quiz backend /fcm-test/*
  -> tvcf-notification-be /v1/*
  -> Firebase FCM
```

## Backend

| 파일 | 역할 |
| --- | --- |
| `app/core/config.py` | notification-be URL, path, 테스트 code 환경변수를 읽는다. |
| `app/modules/__init__.py` | `notification_test_router`를 앱에 등록한다. |
| `app/modules/notification_test/router.py` | 프론트가 호출하는 `/fcm-test/*` API를 제공한다. |
| `app/modules/notification_test/service.py` | notification-be로 outbound HTTP 요청을 보낸다. |
| `app/modules/notification_test/schemas.py` | 테스트 API 요청/응답 모델을 정의한다. |

### Backend API

| API | notification-be 호출 |
| --- | --- |
| `GET /fcm-test/config` | 호출 없음. 현재 설정만 반환한다. |
| `POST /fcm-test/register-device` | `POST /v1/devices` |
| `POST /fcm-test/subscribe-definition` | `POST /v1/subscriptions` |
| `POST /fcm-test/send` | `POST /v1/messages:sendUser` |
| `POST /fcm-test/send-definition` | `POST /v1/messages:sendDefinition` |

### 사용자 매핑

`router.py`는 Coding_Quiz 로그인 사용자를 확인하고 `username`을 notification-be `UserId`로 사용한다.

```text
Coding_Quiz User.username
= notification-be User_TM.UserId
```

`username`이 없거나 20자를 초과하면 테스트 API는 실패한다.

### notification-be 요청 방식

디바이스 등록:

```text
POST /v1/devices
Cookie: access_token=<JWT with userId=username>
User-Agent: <browser user-agent>

{ "registration_token": "<FCM token>" }
```

구독 등록:

```json
{
  "user_id": "<username>",
  "definition_code": "<NotificationDefinition code>"
}
```

유저 직접 발송:

```json
{
  "user_id": "<username>",
  "template_code": "<NotificationTemplate code>"
}
```

구독 기반 발송:

```json
{
  "definition_code": "<NotificationDefinition code>",
  "template_code": "<NotificationTemplate code>"
}
```

notification-be가 오류를 반환하면 Coding_Quiz backend는 `502`로 감싸서 프론트에 보여준다.

## Frontend

| 파일 | 역할 |
| --- | --- |
| `frontend/api/notificationTest.js` | Coding_Quiz backend `/fcm-test/*` 호출 함수 |
| `frontend/app/fcm-test/page.js` | token 발급, 등록, 구독, 발송, foreground 수신 UI |
| `frontend/app/fcm-test/page.module.css` | `/fcm-test` 화면 스타일 |
| `frontend/public/firebase-messaging-sw.js` | Firebase Messaging token 발급에 필요한 service worker |
| `frontend/package.json` | `firebase` 의존성 포함 |

프론트는 notification-be를 직접 호출하지 않는다.
항상 Coding_Quiz backend를 거친다.

## 테스트

`tests/test_notification_test_api.py`는 notification-be 서버를 실제로 띄우지 않고 outbound HTTP 요청을 mock으로 검증한다.

주요 검증:

- `/fcm-test/config` 설정 응답
- 로그인 username을 notification-be `UserId`로 사용하는지
- `/v1/devices`, `/v1/subscriptions`, `/v1/messages:sendUser`, `/v1/messages:sendDefinition` 요청 URL/body/header
- notification-be 오류가 `502`로 변환되는지
- `FCM_TEST_PROXY_ENABLED=false`일 때 테스트 API가 막히는지

실행:

```bash
python -m pytest tests/test_notification_test_api.py -q
```

## 환경변수

Backend `.env.example`:

```text
FCM_TEST_PROXY_ENABLED
TVCF_NOTIFICATION_BASE_URL
TVCF_NOTIFICATION_DEVICE_PATH
TVCF_NOTIFICATION_SUBSCRIPTION_PATH
TVCF_NOTIFICATION_SEND_USER_PATH
TVCF_NOTIFICATION_SEND_DEFINITION_PATH
TVCF_NOTIFICATION_AUTH_TOKEN
TVCF_NOTIFICATION_USER_AGENT
TVCF_NOTIFICATION_TIMEOUT_SECONDS
FCM_TEST_TEMPLATE_CODE
FCM_TEST_DEFINITION_CODE
```

Frontend `frontend/.env.example`:

```text
NEXT_PUBLIC_API_URL
NEXT_PUBLIC_FIREBASE_API_KEY
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
NEXT_PUBLIC_FIREBASE_PROJECT_ID
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
NEXT_PUBLIC_FIREBASE_APP_ID
NEXT_PUBLIC_FIREBASE_VAPID_KEY
NEXT_PUBLIC_NOTIFICATION_TEST_TEMPLATE_CODE
NEXT_PUBLIC_NOTIFICATION_TEST_DEFINITION_CODE
```

## 하지 않는 일

- Coding_Quiz가 Firebase Admin SDK로 직접 FCM을 발송하지 않는다.
- Coding_Quiz가 notification-be DB를 직접 수정하지 않는다.
- `/fcm-test`에서 user id를 직접 입력하지 않는다.

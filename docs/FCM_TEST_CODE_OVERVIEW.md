# FCM 테스트 코드 구성

이 문서는 `Coding_Quiz`에 추가된 FCM 테스트 관련 코드가 어디에 있고, 각 파일이 어떤 역할을 하는지 정리합니다.

목적은 `Coding_Quiz`가 직접 FCM을 발송하는 것이 아니라, 실제 서비스 프로젝트처럼 `tvcf-notification-be`에 token 등록과 발송 요청을 보내는 흐름을 확인하는 것입니다.

```text
Coding_Quiz frontend
  -> Coding_Quiz backend
  -> tvcf-notification-be
  -> Firebase FCM
  -> 브라우저 foreground 수신
```

## 백엔드 코드

### `app/core/config.py`

FCM 테스트 프록시가 사용할 환경변수를 읽습니다.

주요 설정:

```text
FCM_TEST_PROXY_ENABLED
TVCF_NOTIFICATION_BASE_URL
TVCF_NOTIFICATION_DEVICE_PATH
TVCF_NOTIFICATION_SEND_USER_PATH
TVCF_NOTIFICATION_SEND_DEFINITION_PATH
TVCF_NOTIFICATION_AUTH_TOKEN
TVCF_NOTIFICATION_USER_AGENT
TVCF_NOTIFICATION_TIMEOUT_SECONDS
FCM_TEST_TEMPLATE_CODE
FCM_TEST_DEFINITION_CODE
```

`FCM_TEST_PROXY_ENABLED`는 운영 환경에서 기본적으로 꺼지도록 구성되어 있습니다.

### `app/modules/__init__.py`

`notification_test_router`를 FastAPI 앱에 등록합니다.

등록되는 prefix:

```text
/fcm-test
```

### `app/modules/notification_test/router.py`

프론트가 호출하는 FCM 테스트 API를 제공합니다.

제공 API:

```text
GET  /fcm-test/config
POST /fcm-test/register-device
POST /fcm-test/send
POST /fcm-test/send-definition
```

역할:

- Coding_Quiz 로그인 토큰을 확인합니다.
- 로그인한 사용자의 `username`을 notification-be의 `UserId`로 사용합니다.
- token 등록 요청을 notification-be `/v1/devices`로 전달합니다.
- 발송 요청을 notification-be `/v1/messages:sendUser`로 전달합니다.
- 구독 기반 발송 요청을 notification-be `/v1/messages:sendDefinition`으로 전달합니다.

현재 기준:

```text
Coding_Quiz 로그인 username
= notification-be User_TM.UserId
= /v1/messages:sendUser body.user_id
```

### `app/modules/notification_test/service.py`

notification-be로 실제 HTTP 요청을 보내는 서비스입니다.

디바이스 등록:

```text
POST {TVCF_NOTIFICATION_BASE_URL}/v1/devices
Cookie: access_token=<JWT>
User-Agent: CodingQuiz-FCM-Test/1.0

{
  "registration_token": "<FCM token>"
}
```

여기서 `access_token`은 Coding_Quiz 백엔드가 테스트용으로 생성합니다.
JWT payload의 `userId`에는 로그인 사용자의 `username`이 들어갑니다.

발송 요청:

```text
POST {TVCF_NOTIFICATION_BASE_URL}/v1/messages:sendUser

{
  "user_id": "<Coding_Quiz username>",
  "template_code": "<NotificationTemplate code>"
}
```

구독 기반 발송 요청:

```text
POST {TVCF_NOTIFICATION_BASE_URL}/v1/messages:sendDefinition

{
  "definition_code": "<NotificationDefinition code>",
  "template_code": "<NotificationTemplate code>"
}
```

### `app/modules/notification_test/schemas.py`

`/fcm-test` API의 요청/응답 모델을 정의합니다.

포함 모델:

- 설정 응답
- token 등록 요청/응답
- 발송 요청/응답
- 구독 기반 발송 요청/응답
- notification-be 응답 래퍼

## 프론트엔드 코드

### `frontend/api/notificationTest.js`

프론트에서 Coding_Quiz 백엔드의 `/fcm-test` API를 호출하는 클라이언트입니다.

역할:

- `GET /fcm-test/config`
- `POST /fcm-test/register-device`
- `POST /fcm-test/send`
- `POST /fcm-test/send-definition`
- `localStorage`의 로그인 토큰을 `Authorization: Bearer ...` 헤더로 전달

즉 프론트는 notification-be를 직접 호출하지 않고, 항상 Coding_Quiz 백엔드를 거칩니다.

### `frontend/app/fcm-test/page.js`

브라우저에서 실제 테스트를 수행하는 화면입니다.

화면에서 하는 일:

1. Firebase Web SDK 설정 확인
2. 브라우저 알림 권한 요청
3. Firebase `getToken()`으로 FCM registration token 발급
4. 발급된 token을 Coding_Quiz 백엔드에 등록 요청
5. Coding_Quiz 백엔드에 유저 직접 발송 또는 구독 기반 발송 요청
6. foreground `onMessage`로 수신 payload 표시

이 화면은 로그인 후 사용하는 것을 기준으로 합니다.
발송 대상 user id는 직접 입력하지 않고, 백엔드에서 로그인 사용자의 `username`으로 결정합니다.

### `frontend/app/fcm-test/page.module.css`

`/fcm-test` 화면의 레이아웃과 패널 스타일을 정의합니다.

주요 영역:

- token 발급
- token 등록과 notification-be 연결 정보
- 유저 직접 발송
- 구독 기반 발송
- foreground 수신 로그

### `frontend/public/firebase-messaging-sw.js`

Firebase Messaging을 사용하기 위한 service worker입니다.

현재 역할:

- Firebase compat SDK 로드
- 프론트에서 전달받은 Firebase config로 messaging 초기화
- `getToken()`이 service worker registration을 사용할 수 있게 준비

현재 테스트 목적은 foreground 수신 확인이므로, background 알림 표시 로직은 넣지 않았습니다.

### `frontend/package.json`

Firebase Web SDK 의존성이 추가되어 있습니다.

```text
firebase
```

## 테스트 코드

### `tests/test_notification_test_api.py`

Coding_Quiz 백엔드가 notification-be 규칙에 맞게 요청을 만드는지 검증합니다.

검증 범위:

- 설정 API 응답
- 로그인 사용자의 `username`을 notification-be `UserId`로 사용하는지
- token 등록 요청이 `/v1/devices`로 전달되는지
- 등록 요청에 access token cookie가 들어가는지
- 발송 요청이 `/v1/messages:sendUser`로 전달되는지
- 구독 기반 발송 요청이 `/v1/messages:sendDefinition`으로 전달되는지
- template code가 body 또는 환경변수에서 적용되는지
- definition code가 body 또는 환경변수에서 적용되는지
- notification-be 오류가 502 응답으로 감싸지는지
- 프록시 비활성화 시 테스트 API가 막히는지

이 테스트는 Firebase나 notification-be 서버를 실제로 띄우지 않고, outbound HTTP 요청을 mock으로 확인합니다.

## 환경변수 파일

### `.env.example`

Coding_Quiz 백엔드에서 notification-be를 호출하기 위한 값이 정리되어 있습니다.

주요 값:

```text
FCM_TEST_PROXY_ENABLED
TVCF_NOTIFICATION_BASE_URL
TVCF_NOTIFICATION_DEVICE_PATH
TVCF_NOTIFICATION_SEND_USER_PATH
TVCF_NOTIFICATION_SEND_DEFINITION_PATH
TVCF_NOTIFICATION_USER_AGENT
TVCF_NOTIFICATION_TIMEOUT_SECONDS
FCM_TEST_TEMPLATE_CODE
FCM_TEST_DEFINITION_CODE
```

### `frontend/.env.example`

브라우저에서 Firebase Web SDK를 초기화하기 위한 public env가 정리되어 있습니다.

주요 값:

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

## 전체 동작 순서

1. 사용자가 Coding_Quiz에 로그인합니다.
2. `/fcm-test` 페이지에 들어갑니다.
3. 프론트가 `/fcm-test/config`로 테스트 설정을 읽습니다.
4. 사용자가 `FCM token 발급`을 누릅니다.
5. 브라우저가 알림 권한을 허용하면 Firebase `getToken()`으로 token을 받습니다.
6. 사용자가 `Token 등록`을 누릅니다.
7. Coding_Quiz 백엔드는 로그인 사용자의 `username`으로 notification-be용 JWT를 만들고 `/v1/devices`를 호출합니다.
8. 사용자가 `sendUser 발송 요청` 또는 `sendDefinition 발송 요청`을 누릅니다.
9. Coding_Quiz 백엔드는 `sendUser`면 username/template code로 `/v1/messages:sendUser`를 호출합니다.
10. Coding_Quiz 백엔드는 `sendDefinition`이면 definition code/template code로 `/v1/messages:sendDefinition`을 호출합니다.
11. notification-be가 Firebase FCM으로 발송합니다.
12. `/fcm-test` 페이지가 열려 있으면 foreground 수신 로그에 payload가 표시됩니다.

## 이 코드가 하지 않는 일

- Coding_Quiz가 FCM을 직접 발송하지 않습니다.
- Coding_Quiz가 notification-be DB를 직접 수정하지 않습니다.
- `/fcm-test` 화면에서 user id를 직접 입력하지 않습니다.
- background 알림 표시는 테스트 범위에 포함하지 않습니다.

# Coding_Quiz FCM 로컬 테스트

이 문서는 `Coding_Quiz` 화면으로 `tvcf-notification-be`의 FCM 발송을 확인하는 절차만 정리한다.

`Coding_Quiz`는 알림 서버가 아니다. 테스트용 프론트/백엔드 역할만 하고, 실제 발송은 `tvcf-notification-be`가 한다.

## 테스트 흐름

```text
Coding_Quiz frontend
  -> FCM token 발급
  -> Coding_Quiz backend 호출

Coding_Quiz backend
  -> 로그인 username 확인
  -> notification-be에 token 등록, 구독 등록, 발송 요청 전달

tvcf-notification-be
  -> DB에서 user/template/definition/device 조회
  -> Firebase Admin SDK로 FCM 발송

브라우저
  -> /fcm-test 화면의 foreground 로그에서 수신 확인
```

## 사용자 기준

현재 테스트에서는 Coding_Quiz 로그인 `username`을 notification-be 사용자 id로 사용한다.

```text
Coding_Quiz User.username
= notification-be User_TM.UserId
= NotificationDevice_TM.UserId
= NotificationSubscription_TM.UserId
```

예를 들어 Coding_Quiz에서 `seed_user_001`로 로그인했다면 notification-be DB의 `User_TM.UserId`에도 `seed_user_001`이 있어야 한다.

## 필요한 notification-be 데이터

테스트 전에 notification-be DB에 아래 값은 준비되어 있어야 한다.

```text
User_TM.UserId = Coding_Quiz 로그인 username
NotificationTemplate_TM.Code = 테스트 template code
NotificationDefinition_TM.Code = 테스트 definition code
```

아래 데이터는 `/fcm-test` 화면에서 생성하거나 발송 중 생성된다.

```text
NotificationDevice_TM
NotificationSubscription_TM
NotificationMessage_TM
```

## 환경변수

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
FCM_TEST_TEMPLATE_CODE=d6aa9a90-086e-464d-ba62-909dea8e2421
FCM_TEST_DEFINITION_CODE=d6b60268-1737-4b31-87ab-2636bf79c0c4
```

Coding_Quiz frontend `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...
NEXT_PUBLIC_FIREBASE_VAPID_KEY=...
NEXT_PUBLIC_NOTIFICATION_TEST_TEMPLATE_CODE=d6aa9a90-086e-464d-ba62-909dea8e2421
NEXT_PUBLIC_NOTIFICATION_TEST_DEFINITION_CODE=d6b60268-1737-4b31-87ab-2636bf79c0c4
```

notification-be 실행 환경:

```env
GOOGLE_APPLICATION_CREDENTIALS=<Firebase service account JSON 경로>
GOOGLE_CLOUD_PROJECT=<Firebase project id>
```

Firebase 값 준비는 [FCM Console Setup Guide](./FCM_CONSOLE_SETUP.md)를 참고한다.

## 서버 실행

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

브라우저:

```text
http://localhost:3000/fcm-test
```

## 화면 테스트 순서

1. Coding_Quiz에 로그인한다.
2. `/fcm-test`로 이동한다.
3. `FCM token 발급`을 누른다.
4. `Token 등록`을 누른다.
5. 구독 기반 발송을 볼 경우 `Definition 구독 등록`을 누른다.
6. `sendUser 발송 요청` 또는 `sendDefinition 발송 요청`을 누른다.
7. `Foreground 수신 로그`에서 title/body를 확인한다.

## 성공 기준

발송 응답:

```text
target_count = 1
success_count = 1
failure_count = 0
```

화면 수신:

```text
Foreground 수신 로그에 title/body payload 표시
```

## 화면별 역할

| 화면 영역 | 역할 |
| --- | --- |
| 1. Token 발급 | 브라우저 알림 권한을 받고 FCM token을 발급한다. |
| 2. Token 등록 | 로그인 username 기준으로 notification-be `/v1/devices`에 token을 등록한다. |
| 3. 구독 등록 | 로그인 username과 definition code를 `/v1/subscriptions`에 등록한다. |
| 4. 유저 직접 발송 | `/v1/messages:sendUser`로 로그인 사용자에게 직접 발송한다. |
| 5. 구독 기반 발송 | `/v1/messages:sendDefinition`으로 해당 definition 구독자에게 발송한다. |
| 6. Foreground 수신 로그 | 현재 열린 브라우저 탭에서 받은 FCM payload를 표시한다. |

## 다시 테스트할 때 DB 정리

특정 테스트 사용자의 device/subscription/message만 다시 지우고 싶을 때 사용한다.

```sql
DECLARE @UserId NVARCHAR(20) = N'seed_user_001';
DECLARE @DefinitionCode UNIQUEIDENTIFIER = 'd6b60268-1737-4b31-87ab-2636bf79c0c4';

DELETE m
FROM dbo.NotificationMessage_TM AS m
JOIN dbo.NotificationDevice_TM AS d ON d.Id = m.DeviceId
WHERE d.UserId = @UserId;

DELETE s
FROM dbo.NotificationSubscription_TM AS s
JOIN dbo.NotificationDefinition_TM AS def ON def.Id = s.DefinitionId
WHERE s.UserId = @UserId
  AND def.Code = @DefinitionCode;

DELETE FROM dbo.NotificationDevice_TM
WHERE UserId = @UserId;
```

`User_TM`, `NotificationTemplate_TM`, `NotificationDefinition_TM`은 테스트 기준 데이터이므로 지우지 않는다.

## 테스트 범위

이 문서는 `/fcm-test` 화면에서 열린 브라우저 탭의 foreground 수신 확인만 다룬다.

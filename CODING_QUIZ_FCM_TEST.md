# Coding_Quiz FCM Local Test Guide

이 문서는 로컬에서 `Coding_Quiz`를 테스트 클라이언트로 사용해 `tvcf-notification-be`의 foreground FCM 발송 흐름을 검증하는 방법을 정리한다.

핵심은 `Coding_Quiz`가 직접 FCM을 발송하지 않는다는 점이다.

```text
Coding_Quiz frontend
  -> Coding_Quiz backend
  -> tvcf-notification-be
  -> Firebase Cloud Messaging
  -> Coding_Quiz frontend foreground 수신 로그
```

## 1. 현재 테스트의 목적

이 테스트가 확인하는 것:

```text
1. 브라우저가 Firebase Web SDK로 FCM registration token을 발급받을 수 있는지
2. Coding_Quiz backend가 로그인 유저를 기준으로 token 등록 요청을 만들 수 있는지
3. tvcf-notification-be가 token을 NotificationDevice_TM에 저장할 수 있는지
4. Coding_Quiz backend가 로그인 유저 기준으로 /v1/messages:sendUser를 호출할 수 있는지
5. tvcf-notification-be가 Firebase Admin SDK로 실제 FCM을 발송할 수 있는지
6. /fcm-test 화면이 foreground onMessage()로 payload를 받을 수 있는지
```

이 테스트가 확인하지 않는 것:

```text
운영 SSO 전체 로그인 흐름
실제 도메인 이벤트 정책
background notification 표시
모바일 앱 푸시
production Firebase 프로젝트 연동
```

현재 범위는 foreground 테스트다. `/fcm-test` 페이지를 열어둔 상태에서 수신 로그에 payload가 찍히는지 확인한다.

## 2. 전체 구성

```text
Browser
  |
  | 1. FCM token 발급 / foreground 메시지 수신
  v
Coding_Quiz frontend
  |
  | 2. Authorization: Bearer <Coding_Quiz login token>
  | 3. /fcm-test/register-device
  | 4. /fcm-test/send
  v
Coding_Quiz backend
  |
  | 5. 로그인 JWT 검증
  | 6. User.username을 notification-be User_TM.UserId로 사용
  | 7. notification-be용 임시 JWT { userId: username } 생성
  v
tvcf-notification-be
  |
  | 8. User_TM / NotificationDevice_TM / NotificationTemplate_TM 조회
  v
SQL Server tvcf_dev
  |
  | 9. Firebase Admin SDK send_each_for_multicast()
  v
Firebase Cloud Messaging
  |
  | 10. Web Push payload
  v
Browser foreground onMessage()
```

역할 구분:

```text
Coding_Quiz frontend
  Firebase Web SDK 초기화
  Notification 권한 요청
  FCM token 발급
  Coding_Quiz 로그인 token을 backend 요청에 첨부
  foreground 수신 로그 표시

Coding_Quiz backend
  /fcm-test 테스트 프록시
  Coding_Quiz 로그인 JWT 검증
  User.username을 notification-be UserId로 매핑
  notification-be용 임시 access_token cookie 생성
  notification-be /v1/devices, /v1/messages:sendUser 호출

tvcf-notification-be
  FCM token 저장
  template 조회
  Firebase Admin SDK 발송
  NotificationMessage_TM 발송 결과 저장
```

## 3. 사용자 매핑 규칙

현재 테스트는 화면에서 User ID를 직접 입력하지 않는다.

```text
Coding_Quiz 로그인 유저의 username
  = notification-be User_TM.UserId
  = /v1/messages:sendUser의 user_id
```

따라서 테스트하려는 Coding_Quiz 계정의 `username`과 같은 값이 notification-be DB의 `User_TM.UserId`에 있어야 한다.

주의:

```text
notification-be User_TM.UserId 제약 때문에 username은 20자 이하여야 한다.
username이 비어 있거나 20자를 초과하면 Coding_Quiz backend가 400을 반환한다.
로그인하지 않은 상태에서 Token 등록 또는 발송 요청을 누르면 401을 반환한다.
```

## 4. 로컬 DB 테스트 데이터

notification-be DB에 필요한 데이터:

```text
User_TM
  UserId = <Coding_Quiz 로그인 username>

NotificationTemplate_TM
  Code = <테스트 template_code>
  Title = 예: CodingQuiz FCM Test
  Content = 예: Test message from notification-be.

NotificationDevice_TM
  Token 등록 버튼을 누르면 로그인 username 기준으로 저장됨

NotificationMessage_TM
  발송 후 디바이스별 SUCCESS/FAIL 결과가 저장됨
```

현재 화면에서 template code는 입력할 수 있고, `.env`의 `FCM_TEST_TEMPLATE_CODE`를 기본값으로 사용할 수 있다.

## 5. Coding_Quiz backend 설정

파일:

```text
C:/Users/gram/tvcf/Coding_Quiz/.env
```

필요 값:

```env
FCM_TEST_PROXY_ENABLED=true

TVCF_NOTIFICATION_BASE_URL=http://127.0.0.1:8001
TVCF_NOTIFICATION_DEVICE_PATH=/v1/devices
TVCF_NOTIFICATION_SEND_USER_PATH=/v1/messages:sendUser
TVCF_NOTIFICATION_USER_AGENT=CodingQuiz-FCM-Test/1.0
TVCF_NOTIFICATION_TIMEOUT_SECONDS=10

FCM_TEST_TEMPLATE_CODE=<notification-be NotificationTemplate_TM.Code>
```

선택 값:

```env
TVCF_NOTIFICATION_AUTH_TOKEN=
```

`TVCF_NOTIFICATION_AUTH_TOKEN`은 notification-be에 별도 server-to-server 인증이 생겼을 때 `Authorization: Bearer ...`로 전달하기 위한 값이다. 현재 로컬 디바이스 등록의 사용자 식별은 이 값이 아니라 Coding_Quiz 로그인 유저의 `username`으로 만든 임시 JWT가 담당한다.

이제 Coding_Quiz backend가 로그인 JWT를 검증한 뒤 직접 아래 payload의 notification-be용 임시 JWT를 만든다.

```json
{
  "userId": "<Coding_Quiz 로그인 username>",
  "exp": "<10분 뒤 만료 시각>"
}
```

이 token은 `/v1/devices` 호출 시 cookie로만 전달된다.

```http
Cookie: access_token=<Coding_Quiz backend가 만든 notification-be용 JWT>
```

설정 확인:

```text
http://127.0.0.1:8000/fcm-test/config
```

정상 예:

```json
{
  "enabled": true,
  "notification_base_url": "http://127.0.0.1:8001",
  "device_path": "/v1/devices",
  "send_user_path": "/v1/messages:sendUser",
  "default_template_code": "<notification-be template code>"
}
```

`.env`를 수정한 뒤에는 Coding_Quiz backend를 재시작한다.

## 6. Coding_Quiz frontend 설정

파일:

```text
C:/Users/gram/tvcf/Coding_Quiz/frontend/.env.local
```

필요 값:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

NEXT_PUBLIC_NOTIFICATION_TEST_TEMPLATE_CODE=<notification-be NotificationTemplate_TM.Code>

NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=coding-quiz-fcm-test
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...
NEXT_PUBLIC_FIREBASE_VAPID_KEY=...
```

화면의 User ID는 직접 입력하지 않는다. Token 등록 또는 발송 요청이 성공하면 backend 응답의 `notification_user_id`가 화면에 표시된다.

`.env.local`을 수정한 뒤에는 frontend를 재시작한다.

## 7. 서버 실행 순서

터미널 1, `tvcf-notification-be`:

```bash
cd ~/tvcf/tvcf-notification-be
source .venv/Scripts/activate

export GOOGLE_APPLICATION_CREDENTIALS="C:/Users/gram/Desktop/coding-quiz-fcm-test-firebase-adminsdk.json"
export GOOGLE_CLOUD_PROJECT="coding-quiz-fcm-test"

uvicorn app.main:app --reload --port 8001
```

터미널 2, `Coding_Quiz backend`:

```bash
cd ~/tvcf/Coding_Quiz
source .venv/Scripts/activate

uvicorn main:app --reload --port 8000
```

터미널 3, `Coding_Quiz frontend`:

```bash
cd ~/tvcf/Coding_Quiz/frontend
npm run dev
```

브라우저:

```text
http://localhost:3000
```

먼저 Coding_Quiz에 로그인한 뒤 아래로 이동한다.

```text
http://localhost:3000/fcm-test
```

## 8. 화면 버튼별 실제 동작

### 8.1 FCM token 발급

버튼:

```text
FCM token 발급
```

실제 동작:

```text
1. Notification API 지원 여부 확인
2. Service Worker 지원 여부 확인
3. localhost 또는 HTTPS secure context 확인
4. Notification.requestPermission()
5. granted이면 Firebase Web SDK 초기화
6. firebase-messaging-sw.js 등록 및 초기화
7. onMessage() foreground listener 등록
8. getToken(messaging, { vapidKey, serviceWorkerRegistration }) 호출
9. FCM registration token을 화면에 표시
```

이 단계에서는 DB 저장이 없다.

실제 서비스의 최초 발급 시점:

```text
로그인 완료
  -> 사용자가 알림 받기 ON
  -> 브라우저 권한 granted
  -> getToken()
```

이후에는 앱 시작 또는 알림 설정 화면에서 token 변경 여부 확인용으로 `getToken()`을 다시 호출할 수 있다.

### 8.2 Token 등록

버튼:

```text
Token 등록
```

실제 동작:

```text
Coding_Quiz frontend
  -> POST http://127.0.0.1:8000/fcm-test/register-device
  -> Authorization: Bearer <Coding_Quiz login token>
  -> body: { registration_token }

Coding_Quiz backend
  -> login token 검증
  -> User.username 조회
  -> username을 notification-be UserId로 검증
  -> notification-be용 임시 JWT { userId: username } 생성
  -> POST http://127.0.0.1:8001/v1/devices
  -> Cookie: access_token=<임시 JWT>
  -> User-Agent: 원본 브라우저 User-Agent
  -> body: { registration_token }

tvcf-notification-be
  -> access_token cookie에서 userId 읽기
  -> User_TM에서 userId 조회
  -> NotificationDevice_TM에 FCM token 저장 또는 기존 token 처리
```

등록 시점:

```text
getToken()으로 token을 받은 직후
이전에 같은 user/env/token으로 등록 성공한 기록이 없을 때
또는 기존 등록 token과 현재 token이 다를 때
```

중복 등록:

```text
같은 token을 다시 등록하면 현재 notification-be 정책에 따라 Device already exists가 나올 수 있다.
테스트에서는 이미 등록된 상태로 보고 발송 단계로 넘어가면 된다.
운영에서는 같은 token 재등록이 실패로 보이지 않도록 idempotent하게 처리하는 것이 좋다.
```

### 8.3 CodingQuiz 백엔드로 발송 요청

버튼:

```text
CodingQuiz 백엔드로 발송 요청
```

실제 동작:

```text
Coding_Quiz frontend
  -> POST http://127.0.0.1:8000/fcm-test/send
  -> Authorization: Bearer <Coding_Quiz login token>
  -> body: { template_code }

Coding_Quiz backend
  -> login token 검증
  -> User.username을 user_id로 사용
  -> POST http://127.0.0.1:8001/v1/messages:sendUser
  -> body: { user_id: username, template_code }

tvcf-notification-be
  -> User_TM에서 user_id 확인
  -> NotificationTemplate_TM에서 template_code 확인
  -> NotificationDevice_TM에서 user_id의 FCM token 조회
  -> Firebase Admin SDK로 FCM 발송
  -> NotificationMessage_TM에 결과 저장
```

정상 응답:

```json
{
  "message_type": "user",
  "target_count": 1,
  "success_count": 1,
  "failure_count": 0
}
```

## 9. Foreground 수신 확인

현재 테스트는 background notification 표시를 사용하지 않는다.

확인 위치:

```text
http://localhost:3000/fcm-test
  -> 4. Foreground 수신 로그
```

정상 수신 예:

```text
foreground
CodingQuiz FCM Test
Test message from notification-be.
```

이 영역에 아래처럼 JSON 에러가 보이면 수신 로그가 아니라 발송 요청 실패 로그다.

```json
{
  "message": "notification-be returned an error response.",
  "notification_status_code": 500
}
```

## 10. 정상 테스트 순서

```text
1. notification-be DB에 Coding_Quiz 로그인 username과 같은 User_TM.UserId를 준비
2. notification-be DB에 테스트 NotificationTemplate_TM 준비
3. notification-be를 Firebase env와 함께 실행
4. Coding_Quiz backend 실행
5. Coding_Quiz frontend 실행
6. 브라우저에서 Coding_Quiz 로그인
7. /fcm-test 접속
8. FCM token 발급
9. Token 등록
10. Device already exists가 나오면 이미 등록된 상태로 보고 다음 단계 진행
11. CodingQuiz 백엔드로 발송 요청
12. target_count=1, success_count=1, failure_count=0 확인
13. Foreground 수신 로그에서 메시지 확인
```

## 11. 자주 나오는 에러

### 11.1 401, FCM 테스트는 Coding_Quiz 로그인이 필요합니다.

의미:

```text
/fcm-test/register-device 또는 /fcm-test/send 요청에 Coding_Quiz 로그인 token이 없다.
```

확인:

```text
1. Coding_Quiz에 로그인했는지
2. 브라우저 localStorage에 token이 있는지
3. NEXT_PUBLIC_API_URL이 현재 backend 주소인지
```

### 11.2 400, User_TM.UserId는 20자 이하입니다.

의미:

```text
Coding_Quiz 로그인 유저의 username이 notification-be User_TM.UserId 제약보다 길다.
```

해결:

```text
20자 이하 username을 가진 테스트 계정으로 로그인한다.
notification-be User_TM에도 같은 UserId를 준비한다.
```

### 11.3 User not found

의미:

```text
notification-be가 access_token cookie의 userId를 User_TM에서 찾지 못했다.
현재 userId는 Coding_Quiz 로그인 username이다.
```

확인:

```text
1. Coding_Quiz 로그인 username이 무엇인지 확인
2. notification-be DB의 User_TM.UserId에 같은 값이 있는지 확인
3. tvcf-notification-be가 올바른 DB에 붙어 있는지 확인
```

### 11.4 Device already exists

의미:

```text
같은 FCM token이 이미 NotificationDevice_TM에 등록되어 있다.
```

테스트 관점에서는 치명적 실패가 아니다. 이미 등록된 상태라면 바로 발송 요청으로 넘어간다.

운영 관점:

```text
브라우저 재접속, localStorage 삭제, 다중 탭, 재시도 때문에 중복 등록 요청은 항상 발생할 수 있다.
notification-be 또는 각 서비스 backend는 중복 등록에 안전해야 한다.
```

### 11.5 target_count가 0

의미:

```text
발송 user_id에 등록된 활성 FCM token이 없다.
현재 발송 user_id는 Coding_Quiz 로그인 username이다.
```

확인:

```text
1. Token 등록을 먼저 했는지
2. Token 등록과 발송 요청을 같은 Coding_Quiz 로그인 계정으로 했는지
3. NotificationDevice_TM.UserId가 로그인 username과 같은지
4. NotificationDevice_TM.State가 활성 상태인지
```

### 11.6 sendUser에서 500 Internal Server Error

가장 흔한 원인:

```text
현재 실행 중인 notification-be 프로세스에 Firebase Admin SDK env가 없음
```

해결:

```bash
cd ~/tvcf/tvcf-notification-be
source .venv/Scripts/activate

export GOOGLE_APPLICATION_CREDENTIALS="C:/Users/gram/Desktop/coding-quiz-fcm-test-firebase-adminsdk.json"
export GOOGLE_CLOUD_PROJECT="coding-quiz-fcm-test"

uvicorn app.main:app --reload --port 8001
```

주의:

```text
export는 uvicorn 실행 전에 같은 터미널에서 해야 한다.
다른 터미널에 export한 값은 현재 uvicorn 프로세스에 적용되지 않는다.
```

### 11.7 Project ID is required to access Cloud Messaging service

의미:

```text
Firebase Admin SDK가 project id 또는 service account credentials를 찾지 못했다.
```

확인:

```text
1. GOOGLE_APPLICATION_CREDENTIALS 파일 경로가 맞는지
2. GOOGLE_CLOUD_PROJECT가 Firebase projectId와 같은지
3. service account JSON의 project_id가 frontend projectId와 같은지
4. notification-be를 env 설정 후 재시작했는지
```

### 11.8 failure_count가 1

의미:

```text
Firebase까지 요청은 갔지만 개별 token 발송이 실패했다.
```

확인:

```text
1. frontend Firebase config와 service account JSON이 같은 Firebase 프로젝트인지
2. 브라우저 token이 현재 Firebase 프로젝트에서 발급된 token인지
3. 오래된 token이면 FCM token을 다시 발급하고 다시 등록했는지
4. 브라우저 알림 권한이 granted인지
```

## 12. 빠른 점검

Coding_Quiz backend 설정 확인:

```bash
curl http://127.0.0.1:8000/fcm-test/config
```

정상 설정 기준:

```json
{
  "enabled": true,
  "notification_base_url": "http://127.0.0.1:8001",
  "device_path": "/v1/devices",
  "send_user_path": "/v1/messages:sendUser",
  "default_template_code": "<notification-be template code>"
}
```

notification-be template 확인:

```bash
curl http://127.0.0.1:8001/v1/templates
```

## 13. 현재 테스트에서 가장 중요한 기준

```text
Coding_Quiz 로그인 username
  = notification-be User_TM.UserId
  = NotificationDevice_TM.UserId
  = /v1/messages:sendUser body.user_id
```

이 값이 서로 맞아야 token 등록, FCM 발송, foreground 수신까지 이어진다.

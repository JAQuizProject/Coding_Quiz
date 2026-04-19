# Coding_Quiz FCM Local Test Guide

이 문서는 로컬에서 `Coding_Quiz`를 테스트 클라이언트로 사용해 `tvcf-notification-be`의 FCM 발송 흐름을 검증하는 방법을 정리한다.

핵심은 `Coding_Quiz`가 직접 알림을 보내는 것이 아니라, `Coding_Quiz backend`가 `tvcf-notification-be`에 요청하고 `tvcf-notification-be`가 DB와 Firebase Admin SDK를 이용해 실제 FCM을 보내는 구조라는 점이다.

## 1. 이 테스트의 목적

이 테스트가 확인하는 것:

```text
Coding_Quiz 화면에서 버튼 클릭
  -> Coding_Quiz backend가 notification-be에 요청
  -> notification-be가 DB에서 유저/디바이스/템플릿 조회
  -> notification-be가 Firebase Admin SDK로 FCM 발송
  -> 브라우저가 FCM 메시지 수신
```

이 테스트가 확인하지 않는 것:

```text
FCM Notifications composer 직접 발송 테스트
운영 로그인/권한 플로우
Coding_Quiz의 실제 서비스 알림 정책
모바일 앱 푸시
production Firebase 프로젝트 연동
```

즉 지금 테스트는 "각 서비스 백엔드가 공통 알림 서버인 `tvcf-notification-be`에 붙으면 실제 FCM까지 갈 수 있는가"를 확인하는 로컬 e2e 테스트다.

## 2. 전체 구성

```text
Browser
  |
  | 1. FCM token 발급 / foreground 메시지 수신
  v
Coding_Quiz frontend
  |
  | 2. /fcm-test/register-device
  | 3. /fcm-test/send
  v
Coding_Quiz backend
  |
  | 4. /v1/devices
  | 5. /v1/messages:sendUser
  v
tvcf-notification-be
  |
  | 6. User_TM / NotificationDevice_TM / NotificationTemplate_TM 조회
  v
SQL Server tvcf_dev
  |
  | 7. Firebase Admin SDK send_each_for_multicast()
  v
Firebase Cloud Messaging
  |
  | 8. Web Push
  v
Browser
```

역할을 나누면 아래와 같다.

```text
Coding_Quiz frontend
  테스트 화면, Firebase Web SDK, FCM token 발급, foreground 수신 로그 표시

Coding_Quiz backend
  테스트 프록시 서버. 브라우저 요청을 notification-be로 전달

tvcf-notification-be
  실제 알림 서버. DB 조회, token 저장, Firebase Admin SDK 발송

SQL Server tvcf_dev
  User_TM, NotificationDevice_TM, NotificationTemplate_TM, NotificationMessage_TM 저장

Firebase Cloud Messaging
  실제 Web Push 배달
```

## 3. FCM Console 설정 문서

Firebase Console에서 필요한 FCM 프로젝트와 키를 준비하는 절차는 별도 문서에서 관리한다.

참조:

```text
FCM_CONSOLE_SETUP.md
```

이 문서는 이미 준비된 FCM 설정값을 사용해 로컬 foreground 테스트를 실행하는 흐름만 다룬다.

## 4. 로컬 DB 테스트 데이터

현재 로컬 `tvcf_dev` 기준 테스트 값:

```text
User ID:
seed_user_001

Template code:
d6aa9a90-086e-464d-ba62-909dea8e2421

Template title:
CodingQuiz FCM Test

Template content:
Test message from notification-be.
```

관련 DB 테이블:

```text
User_TM
  seed_user_001 유저가 있어야 함

NotificationTemplate_TM
  d6aa9a90-086e-464d-ba62-909dea8e2421 템플릿이 있어야 함

NotificationDevice_TM
  seed_user_001 유저의 FCM token이 저장됨

NotificationMessage_TM
  발송 후 디바이스별 결과가 저장됨
```

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

TVCF_NOTIFICATION_ACCESS_TOKEN=<seed_user_001 userId가 들어있는 local test JWT>

FCM_TEST_USER_ID=seed_user_001
FCM_TEST_TEMPLATE_CODE=d6aa9a90-086e-464d-ba62-909dea8e2421
```

값의 의미:

```text
FCM_TEST_PROXY_ENABLED
  /fcm-test 테스트 API를 켤지 여부

TVCF_NOTIFICATION_BASE_URL
  notification-be 주소

TVCF_NOTIFICATION_DEVICE_PATH
  FCM token 등록 API 경로

TVCF_NOTIFICATION_SEND_USER_PATH
  특정 user_id로 발송 요청하는 API 경로

TVCF_NOTIFICATION_ACCESS_TOKEN
  notification-be /v1/devices가 access_token cookie로 읽는 로컬 테스트 JWT

FCM_TEST_USER_ID
  발송 요청의 기본 user_id

FCM_TEST_TEMPLATE_CODE
  발송 요청의 기본 template_code
```

`TVCF_NOTIFICATION_ACCESS_TOKEN`은 `/v1/devices` 등록에 필요하다.

이 token 안에는 아래 payload가 들어가야 한다.

```json
{
  "userId": "seed_user_001"
}
```

현재 `tvcf-notification-be`의 `app/core/auth.py`는 이 token의 서명을 검증하지 않고 payload의 `userId`를 읽는다.

로컬 테스트용 token을 새로 만들려면 `tvcf-notification-be` 루트에서 아래 명령을 사용한다.

```bash
python - <<'PY'
import jwt

token = jwt.encode(
    {"userId": "seed_user_001"},
    "local-test-secret-for-notification",
    algorithm="HS256",
)
print(token)
PY
```

주의:

```text
Coding_Quiz backend는 실행 중 .env 변경을 자동으로 반영하지 않을 수 있다.
.env를 수정한 뒤에는 backend를 끄고 다시 켠다.
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
  "default_user_id": "seed_user_001",
  "default_template_code": "d6aa9a90-086e-464d-ba62-909dea8e2421",
  "has_notification_access_token": true
}
```

## 6. Coding_Quiz frontend 설정

파일:

```text
C:/Users/gram/tvcf/Coding_Quiz/frontend/.env.local
```

필요 값:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

NEXT_PUBLIC_NOTIFICATION_TEST_USER_ID=seed_user_001
NEXT_PUBLIC_NOTIFICATION_TEST_TEMPLATE_CODE=d6aa9a90-086e-464d-ba62-909dea8e2421

NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=coding-quiz-fcm-test
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...
NEXT_PUBLIC_FIREBASE_VAPID_KEY=...
```

값의 의미:

```text
NEXT_PUBLIC_API_URL
  Coding_Quiz backend 주소

NEXT_PUBLIC_NOTIFICATION_TEST_USER_ID
  화면 input의 기본 User ID

NEXT_PUBLIC_NOTIFICATION_TEST_TEMPLATE_CODE
  화면 input의 기본 Template code

NEXT_PUBLIC_FIREBASE_*
  Firebase Web app config

NEXT_PUBLIC_FIREBASE_VAPID_KEY
  FCM token 발급용 public key
```

주의:

```text
Next.js frontend는 .env.local 변경 후 재시작해야 한다.
```

## 7. 서버 실행 순서

터미널 1, `tvcf-notification-be`:

```bash
cd ~/tvcf/tvcf-notification-be

source .venv/Scripts/activate

export GOOGLE_APPLICATION_CREDENTIALS="C:/Users/gram/Desktop/coding-quiz-fcm-test-firebase-adminsdk-fbsvc-c193426100.json"
export GOOGLE_CLOUD_PROJECT="coding-quiz-fcm-test"

echo $GOOGLE_APPLICATION_CREDENTIALS
echo $GOOGLE_CLOUD_PROJECT

uvicorn app.main:app --reload --port 8001
```

터미널 2, `Coding_Quiz backend`:

```bash
cd ~/tvcf/Coding_Quiz

poetry run uvicorn main:app --reload --port 8000
```

`poetry`가 안 되면:

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
http://localhost:3000/fcm-test
```

## 8. 화면 버튼별 실제 동작

### 8.1 FCM token 발급

화면 버튼:

```text
FCM token 발급
```

실제 동작:

```text
1. 브라우저 Notification 권한 요청
2. Firebase Web SDK 초기화
3. FCM token 발급용 registration 준비
4. getToken()으로 브라우저 FCM registration token 발급
5. onMessage()로 foreground 메시지 수신 대기
```

결과:

```text
브라우저 알림 받을 주소인 FCM token이 textarea에 표시됨
```

이 단계에서는 DB 저장이 없다.

### 8.2 Token 등록

화면 버튼:

```text
Token 등록
```

실제 동작:

```text
Coding_Quiz frontend
  -> POST http://127.0.0.1:8000/fcm-test/register-device

Coding_Quiz backend
  -> POST http://127.0.0.1:8001/v1/devices
  -> Cookie: access_token=<TVCF_NOTIFICATION_ACCESS_TOKEN>

tvcf-notification-be
  -> access_token payload에서 userId 읽기
  -> User_TM에서 userId 조회
  -> NotificationDevice_TM에 FCM token 저장
```

중요:

```text
Token 등록은 화면의 User ID input을 사용하지 않는다.
등록 유저는 TVCF_NOTIFICATION_ACCESS_TOKEN 안의 userId로 결정된다.
```

### 8.3 CodingQuiz 백엔드로 발송 요청

화면 버튼:

```text
CodingQuiz 백엔드로 발송 요청
```

실제 동작:

```text
Coding_Quiz frontend
  -> POST http://127.0.0.1:8000/fcm-test/send
     body: { user_id, template_code }

Coding_Quiz backend
  -> POST http://127.0.0.1:8001/v1/messages:sendUser
     body: { user_id, template_code }

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

## 9. 브라우저 메시지 확인 위치

현재 테스트는 foreground 수신만 확인한다.

여기서 foreground는 `/fcm-test` 페이지를 브라우저에서 열어둔 상태를 말한다.

이번 테스트에서 성공 여부는 `/fcm-test` 화면의 `Foreground 수신 로그`로 판단한다.

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

이 영역에 아래처럼 에러 JSON이 보이면 수신 로그가 아니라 발송 요청 실패 로그다.

```json
{
  "message": "notification-be returned an error response.",
  "notification_status_code": 500
}
```

## 10. 이벤트와 시그널 기준으로 본 흐름

알림은 아무 때나 자동으로 나가는 것이 아니라, 어떤 "시그널" 또는 "이벤트"가 발생했을 때 시작된다.

현재 로컬 테스트에서는 실제 서비스 이벤트 대신 `/fcm-test` 화면의 버튼 클릭이 그 시그널 역할을 한다.

### 10.1 현재 테스트에서의 시그널

```text
사용자 클릭: FCM token 발급
  -> 브라우저가 Firebase에 "이 브라우저로 알림 받을 수 있게 token을 달라"고 요청
  -> 결과로 FCM registration token 생성
```

```text
사용자 클릭: Token 등록
  -> Coding_Quiz frontend가 Coding_Quiz backend에 registration_token 전달
  -> Coding_Quiz backend가 notification-be /v1/devices 호출
  -> notification-be가 access_token cookie에서 userId 확인
  -> notification-be가 NotificationDevice_TM에 token 저장
```

```text
사용자 클릭: CodingQuiz 백엔드로 발송 요청
  -> Coding_Quiz frontend가 Coding_Quiz backend에 user_id/template_code 전달
  -> Coding_Quiz backend가 notification-be /v1/messages:sendUser 호출
  -> notification-be가 DB에서 user/template/device token 조회
  -> notification-be가 Firebase Admin SDK로 FCM 발송
```

```text
Firebase delivery event
  -> 브라우저가 FCM payload 수신
  -> /fcm-test 페이지가 열려 있으면 onMessage() 실행
  -> Foreground 수신 로그에 메시지 표시
```

즉 현재 테스트의 실제 발송 트리거는 아래 버튼이다.

```text
CodingQuiz 백엔드로 발송 요청
```

이 버튼이 실제 서비스에서의 "댓글 생성됨", "입찰 등록됨", "메시지 도착함" 같은 백엔드 이벤트를 대신한다.

### 10.2 실제 서비스에서는 어떤 식으로 바뀌는가

실제 프로젝트에서는 보통 프론트가 notification-be를 직접 호출하지 않는다.

대부분의 구조는 아래와 같다.

```text
사용자 행동
  -> 각 서비스 frontend
  -> 각 서비스 backend
  -> 각 서비스 backend에서 도메인 이벤트 발생
  -> 각 서비스 backend가 notification-be에 발송 요청
  -> notification-be가 FCM 발송
```

예시 1, 댓글 알림:

```text
사용자 A가 게시글에 댓글 작성 버튼 클릭
  -> 서비스 frontend가 서비스 backend에 댓글 생성 요청
  -> 서비스 backend가 댓글을 DB에 저장
  -> 댓글 저장 성공 후 "게시글 작성자에게 댓글 알림 필요" 이벤트 발생
  -> 서비스 backend가 notification-be /v1/messages:sendUser 호출
  -> notification-be가 게시글 작성자의 device token으로 FCM 발송
```

예시 2, 공지/캠페인 알림:

```text
관리자가 공지 발송 버튼 클릭
  -> 서비스 backend가 발송 대상 조건 계산
  -> 대상 사용자가 특정 notification definition을 구독 중인지 확인
  -> 서비스 backend가 notification-be /v1/messages:sendDefinition 호출
  -> notification-be가 구독자들의 device token으로 FCM 발송
```

예시 3, Coding_Quiz에 실제 기능을 붙인다면:

```text
사용자가 퀴즈를 제출
  -> Coding_Quiz backend가 채점 결과 저장
  -> 특정 조건 만족, 예: 만점 달성, 랭킹 변경, 새 배지 획득
  -> Coding_Quiz backend가 "알림이 필요한 이벤트"라고 판단
  -> Coding_Quiz backend가 notification-be /v1/messages:sendUser 호출
  -> notification-be가 FCM 발송
```

### 10.3 프론트와 백엔드의 책임 구분

프론트의 책임:

```text
브라우저 알림 권한 요청
Firebase Web SDK로 FCM token 발급
발급된 token을 자기 backend로 전달
foreground 메시지 표시
```

각 서비스 백엔드의 책임:

```text
사용자 행동을 실제 서비스 이벤트로 확정
DB 저장 성공 여부 판단
누구에게 어떤 알림을 보낼지 결정
notification-be로 발송 요청
```

notification-be의 책임:

```text
유저 존재 여부 확인
FCM token 저장
템플릿 조회
대상 device token 조회
Firebase Admin SDK로 발송
발송 결과 저장
```

Firebase의 책임:

```text
registration token 발급
서버가 보낸 FCM 메시지를 브라우저 Push 서비스로 전달
열려 있는 브라우저 페이지에 payload 전달
```

### 10.4 현재 테스트가 실제 서비스 이벤트를 대신하는 방식

현재 `/fcm-test`는 실제 도메인 이벤트가 없다.

그래서 아래처럼 버튼으로 이벤트를 직접 만든다.

```text
실제 서비스 이벤트
  댓글 작성 완료
  입찰 등록 완료
  새 메시지 도착
  퀴즈 결과 저장 완료

현재 테스트 이벤트
  "CodingQuiz 백엔드로 발송 요청" 버튼 클릭
```

따라서 현재 테스트의 의미는 아래와 같다.

```text
비즈니스 이벤트 판단 로직은 테스트하지 않는다.
대신, 이벤트가 이미 발생했다고 가정하고
각 서비스 backend가 notification-be에 발송 요청했을 때
알림 서버와 Firebase까지 정상 동작하는지 확인한다.
```

## 11. 정상 테스트 순서

```text
1. notification-be를 Firebase env와 함께 재시작
2. Coding_Quiz backend 재시작
3. Coding_Quiz frontend 재시작
4. http://localhost:3000/fcm-test 접속
5. FCM token 발급
6. Token 등록
7. Device already exists가 나오면 이미 등록된 상태로 보고 다음 단계 진행
8. CodingQuiz 백엔드로 발송 요청
9. target_count=1, success_count=1, failure_count=0 확인
10. Foreground 수신 로그에서 메시지 확인
```

## 12. 자주 나오는 에러

### 12.1 User not found

예:

```json
{
  "detail": "User not found"
}
```

의미:

```text
access_token 안의 userId를 tvcf_dev.User_TM에서 찾지 못했다.
```

확인:

```text
1. TVCF_NOTIFICATION_ACCESS_TOKEN payload의 userId가 seed_user_001인지
2. tvcf-notification-be가 tvcf_dev DB에 붙어 있는지
3. Coding_Quiz backend를 .env 수정 후 재시작했는지
4. /fcm-test/config의 default_user_id가 seed_user_001인지
```

### 12.2 Device already exists

예:

```json
{
  "detail": "Device already exists"
}
```

의미:

```text
같은 FCM token이 이미 NotificationDevice_TM에 등록되어 있다.
```

테스트 관점에서는 치명적 실패가 아니다.

이미 등록된 상태라면 바로 발송 요청으로 넘어간다.

### 12.3 target_count가 0

의미:

```text
해당 user_id에 등록된 활성 FCM token이 없다.
```

확인:

```text
1. Token 등록을 먼저 했는지
2. 등록할 때 사용된 access_token의 userId와 발송 user_id가 같은지
3. NotificationDevice_TM.State가 1인지
```

### 12.4 sendUser에서 500 Internal Server Error

화면 예:

```json
{
  "target_url": "http://127.0.0.1:8001/v1/messages:sendUser",
  "notification_status_code": 500,
  "notification_body": "Internal Server Error"
}
```

가장 흔한 원인:

```text
현재 실행 중인 notification-be 프로세스에 Firebase Admin SDK env가 없음
```

해결:

```bash
cd ~/tvcf/tvcf-notification-be

source .venv/Scripts/activate

export GOOGLE_APPLICATION_CREDENTIALS="C:/Users/gram/Desktop/coding-quiz-fcm-test-firebase-adminsdk-fbsvc-c193426100.json"
export GOOGLE_CLOUD_PROJECT="coding-quiz-fcm-test"

uvicorn app.main:app --reload --port 8001
```

주의:

```text
export는 uvicorn 실행 전에 같은 터미널에서 해야 한다.
다른 터미널에 export한 값은 현재 uvicorn 프로세스에 적용되지 않는다.
```

### 12.5 Project ID is required to access Cloud Messaging service

의미:

```text
Firebase Admin SDK가 project id 또는 service account credentials를 찾지 못했다.
```

확인:

```text
1. GOOGLE_APPLICATION_CREDENTIALS 파일 경로가 맞는지
2. GOOGLE_CLOUD_PROJECT가 coding-quiz-fcm-test인지
3. service account JSON의 project_id가 coding-quiz-fcm-test인지
4. notification-be를 env 설정 후 재시작했는지
```

### 12.6 failure_count가 1

의미:

```text
Firebase까지 요청은 갔지만 개별 token 발송이 실패했다.
```

확인:

```text
1. frontend Firebase config와 service account JSON이 같은 Firebase 프로젝트인지
2. 브라우저 token이 현재 프로젝트에서 발급된 token인지
3. 오래된 token이면 FCM token을 다시 발급하고 다시 등록했는지
4. 브라우저 알림 권한이 granted인지
```

## 13. 빠른 점검 명령

notification-be template 확인:

```bash
curl http://127.0.0.1:8001/v1/templates
```

Coding_Quiz backend 설정 확인:

```bash
curl http://127.0.0.1:8000/fcm-test/config
```

정상 설정 기준:

```json
{
  "default_user_id": "seed_user_001",
  "default_template_code": "d6aa9a90-086e-464d-ba62-909dea8e2421",
  "has_notification_access_token": true
}
```

## 14. 현재 로컬에서 확인된 상태

현재까지 확인된 것:

```text
SQL Server localhost:1433 연결 정상
tvcf_dev DB 연결 정상
notification-be Alembic migration 적용 완료
User_TM에 seed_user_001 있음
NotificationTemplate_TM에 테스트 템플릿 있음
/v1/templates 정상 응답
/v1/devices 직접 호출로 FCM token 등록 성공
Firebase env를 명시한 별도 프로세스에서 sendUser success_count=1 확인
```

현재 테스트에서 가장 주의할 점:

```text
브라우저 화면의 500은 대부분 notification-be 실행 env 문제다.
notification-be를 Firebase env와 함께 다시 켜야 한다.
```

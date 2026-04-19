# Notification Project Integration Guide

이 문서는 현재 로컬 테스트가 어디까지 완료됐는지, 그리고 회사의 각 프론트/백엔드 프로젝트가 `tvcf-notification-be`에 연동할 때 각각 무엇을 구현해야 하는지 정리한다.

## 1. 현재 테스트 진행 상태

현재 테스트는 `Coding_Quiz`를 실제 서비스 프로젝트 대신 사용하는 로컬 e2e 테스트다.

목표 흐름:

```text
Coding_Quiz frontend
  -> Coding_Quiz backend
  -> tvcf-notification-be
  -> SQL Server tvcf_dev
  -> Firebase Cloud Messaging
  -> Browser
```

현재 확인된 상태:

```text
SQL Server localhost:1433 연결 정상
tvcf_dev DB 연결 정상
notification-be migration 적용 완료
Coding_Quiz backend /fcm-test/config 설정 정상
notification-be /v1/templates 조회 정상
User_TM에 Coding_Quiz 로그인 username과 같은 UserId 필요
NotificationTemplate_TM에 테스트 템플릿 존재
Token 등록 시 Coding_Quiz 로그인 username 기준으로 NotificationDevice_TM 저장
Firebase env를 명시한 notification-be에서 sendUser success_count=1 확인 가능
```

현재 로컬 DB 기준:

```text
DB:
tvcf_dev

User:
<Coding_Quiz 로그인 username>

Template:
<notification-be NotificationTemplate_TM.Code>

Device token:
Token 등록 버튼 실행 후 <Coding_Quiz 로그인 username> 기준으로 저장됨
```

현재 Coding_Quiz backend 설정 확인 결과:

```json
{
  "enabled": true,
  "notification_base_url": "http://127.0.0.1:8001",
  "device_path": "/v1/devices",
  "send_user_path": "/v1/messages:sendUser",
  "default_template_code": "<notification-be template code>"
}
```

아직 완전히 끝났다고 보기 어려운 부분:

```text
브라우저 /fcm-test 화면에서 foreground 수신 로그 성공 캡처는 아직 확정되지 않음
현재 실행 중인 notification-be가 Firebase env 없이 켜지면 sendUser 500 발생
```

중요:

```text
sendUser가 success_count=1을 반환하는 것과
NotificationMessage_TM에 발송 이력이 영구 저장되는 것은 별개다.
```

현재는 발송 서비스가 `NotificationMessage_TM` 객체를 만든 뒤 `commit()`까지 수행하도록 수정했고, 로컬 `tvcf_dev`에서 이력 저장을 확인했다.

검증 결과:

```text
before_messages=0
sendUser response: target_count=1, success_count=1, failure_count=0
after_messages=1
latest status=SUCCESS
```

현재 Coding_Quiz 테스트에서는 별도 하드코딩 user id나 access token env를 사용하지 않는다.

```text
Coding_Quiz 로그인 JWT
  -> Coding_Quiz backend에서 현재 User 조회
  -> User.username을 notification-be User_TM.UserId로 사용
  -> notification-be용 임시 JWT { userId: username } 생성
  -> /v1/devices Cookie: access_token=<임시 JWT>
```

## 2. 현재 테스트가 의미하는 것

현재 테스트에서 확인하는 것은 아래다.

```text
각 서비스 backend가 notification-be에 발송 요청을 보냈을 때
notification-be가 DB에서 token/template을 찾아
Firebase Admin SDK로 실제 FCM 발송을 수행할 수 있는가
```

현재 수신 확인 방식은 foreground만 대상으로 한다.

```text
/fcm-test 페이지를 열어둔 상태
  -> Firebase Web SDK onMessage()로 payload 수신
  -> 화면의 Foreground 수신 로그에서 확인
```

현재 테스트에서 확인하지 않는 것:

```text
실제 회사 서비스의 로그인 흐름
실제 도메인 이벤트 발생 조건
운영 권한/보안 정책
운영 Firebase 프로젝트 설정
각 서비스별 알림 수신 설정 UI
알림 이력 저장의 commit 보장
```

현재 `Coding_Quiz`의 `/fcm-test` 화면은 실제 업무 이벤트를 대신해 버튼으로 이벤트를 발생시키는 테스트 도구다.

```text
실제 서비스 이벤트:
댓글 작성 완료, 입찰 등록 완료, 새 메시지 도착, 퀴즈 결과 저장 완료

현재 테스트 이벤트:
/fcm-test 화면에서 "CodingQuiz 백엔드로 발송 요청" 버튼 클릭
```

## 3. 회사 프로젝트 연동 시 전체 흐름

회사 프로젝트는 SSO를 사용하고, 각 프로젝트가 같은 `User_TM`을 바라본다는 전제를 둔다.

따라서 알림 서버 기준의 사용자 식별자는 별도 매핑값이 아니라 `User_TM.UserId`다.

```text
SSO login user
  -> 각 서비스 backend에서 현재 사용자 확인
  -> 같은 User_TM.UserId 사용
  -> notification-be도 같은 User_TM.UserId 기준으로 token/template/message 처리
```

이 전제에서는 아래 매핑 테이블이 필요하지 않다.

```text
service_user_id -> notification_user_id 매핑
project_user_id -> User_TM.UserId 매핑
```

각 서비스 backend가 SSO에서 확인한 현재 사용자의 `UserId`를 그대로 notification-be 기준 사용자로 사용하면 된다.

권장 구조:

```text
각 서비스 frontend
  -> 각 서비스 backend
  -> tvcf-notification-be
  -> Firebase Cloud Messaging
  -> 사용자 브라우저/앱
```

프론트가 `tvcf-notification-be`를 직접 호출하는 구조는 권장하지 않는다.

이유:

```text
프론트는 사용자 인증/권한을 직접 notification-be 형식으로 맞추기 어렵다.
FCM token 등록 시 현재 로그인 사용자를 신뢰성 있게 결정해야 한다.
서버 간 인증 토큰을 브라우저에 노출하면 안 된다.
알림 발송 시점은 대부분 backend의 DB 저장 성공 이후에 확정된다.
```

따라서 각 프로젝트는 보통 아래처럼 붙는다.

```text
frontend
  -> "내 FCM token 등록해줘" 요청을 자기 backend에 보냄

backend
  -> SSO에서 확인한 현재 User_TM.UserId와 FCM token을 매핑
  -> notification-be /v1/devices 호출

backend
  -> 도메인 이벤트 발생 시 notification-be /v1/messages:sendUser 또는 /v1/messages:sendDefinition 호출
```

## 4. Frontend가 해야 할 일

각 프론트 프로젝트의 책임은 "브라우저가 알림을 받을 준비"를 하는 것이다.

### 4.1 FCM 설정값 반영

각 frontend는 Firebase Web SDK 초기화 값과 FCM token 발급에 필요한 값을 환경변수로 받는다.

FCM 설정값을 어디서 만들고 어떻게 프로젝트별로 관리하는지는 별도 문서에서 관리한다.

참조:

```text
FCM_CONSOLE_SETUP.md
```

### 4.2 FCM token 발급 준비

현재 테스트는 foreground 수신만 확인한다.

역할:

```text
Firebase Web SDK에서 FCM registration token을 발급
현재 foreground 테스트에서는 onMessage() 수신 확인
```

token 발급은 로그인 전이 아니라 로그인 완료 후에 수행한다. token은 브라우저 주소일 뿐이고, 서버에 저장하려면 어느 `User_TM.UserId`의 token인지 확정되어 있어야 한다.

```text
token만 있음
  -> 어느 사용자의 token인지 모름

로그인 사용자 + token
  -> User_TM.UserId와 token을 연결해 저장 가능
```

### 4.3 알림 권한 요청

브라우저에서 알림 권한을 요청한다.

권장:

```text
페이지 진입 즉시 강제 요청하지 말고
사용자가 알림 받기 버튼을 누르거나
명확한 동의 UI를 거친 뒤 요청
```

필요 상태:

```text
Notification.permission === "granted"
```

권장 최초 흐름:

```text
로그인 완료
  -> 알림 설정 ON 또는 알림 받기 버튼 클릭
  -> Notification.requestPermission()
  -> granted
  -> getToken()
  -> backend에 token 등록 요청
```

### 4.4 FCM token 발급

Firebase Web SDK로 token을 발급한다.

개념 흐름:

```text
initializeApp(firebaseConfig)
getMessaging(app)
getToken(messaging, { vapidKey })
```

결과:

```text
registration_token
```

이 token은 "이 브라우저 인스턴스에 FCM을 보내기 위한 주소"다.

시점은 둘로 나눈다.

```text
최초 발급:
  로그인 완료 후 사용자가 알림 받기 ON
  브라우저 권한 granted
  그 직후 getToken()

이후 확인/갱신:
  로그인 완료 후 앱 시작 시
  또는 알림 설정 화면 진입 시
  알림 설정이 ON이고 Notification.permission이 granted면 getToken()
  이전 등록 token과 다르면 backend에 갱신 등록
```

백엔드는 token 발급을 대신할 수 없다.

```text
백엔드 가능:
  로그인 응답 또는 설정 조회 응답으로 token 등록 필요 상태를 알려줌
  frontend가 보낸 registration_token을 현재 User_TM.UserId와 연결

백엔드 불가:
  브라우저 알림 권한 허용
  브라우저 PushSubscription 생성
  FCM registration token 직접 발급
```

### 4.5 자기 backend에 token 등록 요청

프론트는 `notification-be`로 직접 보내지 말고, 자기 서비스 backend로 보낸다.

예:

```http
POST /me/notification-devices
Authorization: Bearer <service user token>
Content-Type: application/json

{
  "registration_token": "<browser fcm token>"
}
```

프론트가 보내야 할 값:

```text
registration_token
device/browser 정보는 backend 또는 notification-be가 User-Agent로 추론 가능
```

프론트가 보내면 안 되는 값:

```text
server-to-server auth token
Firebase service account JSON
다른 사용자의 user_id
```

등록 요청 시점:

```text
getToken()으로 token을 받은 직후
이전에 같은 user/env/token으로 등록 성공한 기록이 없을 때
기존 등록 token과 현재 token이 다를 때
```

### 4.6 foreground 수신 처리

현재 회사 연동 문서에서 다루는 수신 방식은 foreground다.

```text
페이지가 열려 있고 focus 상태
onMessage()로 payload 수신
화면 toast, 알림 목록 갱신, 카운터 증가 등 처리
```

### 4.7 token 갱신/재등록 처리

FCM token은 영구 고정값으로 보면 안 된다.

다음 상황에서는 token이 바뀔 수 있다.

```text
브라우저 데이터 삭제
알림 권한 변경
Firebase 설정 변경
브라우저/기기 변경
```

프론트는 로그인 완료 후 앱 시작 또는 알림 설정 화면 진입 시 token을 다시 가져오고, 기존 등록과 달라지면 backend에 재등록해야 한다. 단, 프론트의 이전 등록 기록은 최적화일 뿐이다. 서버는 중복 등록 요청이 들어와도 안전해야 한다.

## 5. Backend가 해야 할 일

각 서비스 backend의 책임은 "어떤 사용자에게 어떤 알림을 보낼지 결정"하는 것이다.

### 5.1 SSO 사용자와 FCM token 연결

프론트가 보낸 registration token을 현재 SSO 로그인 사용자와 연결한다.

회사 프로젝트는 같은 `User_TM`을 보므로, backend에서 확인한 SSO 사용자 ID가 곧 notification-be의 `User_TM.UserId`다.

개념 흐름:

```text
frontend -> service backend
  POST /me/notification-devices
  registration_token 전달

service backend
  SSO 세션/토큰으로 현재 User_TM.UserId 확인
notification-be /v1/devices 호출
```

중요:

```text
프론트는 registration_token만 보낸다.
user_id는 backend가 SSO/session/JWT로 확정한다.
프론트가 보낸 user_id를 그대로 믿고 token을 등록하면 안 된다.
```

현재 notification-be의 `/v1/devices`는 `access_token` cookie에서 userId를 읽는다.

현재 로컬 테스트 방식:

```http
POST /v1/devices
Cookie: access_token=<JWT payload에 userId 포함>
Content-Type: application/json

{
  "registration_token": "<fcm token>"
}
```

회사 SSO 기준으로 연동할 때 선택지는 아래다.

```text
1. 각 서비스 backend가 사용자의 SSO access_token cookie를 notification-be로 전달
   - notification-be가 같은 SSO token에서 User_TM.UserId를 읽을 수 있어야 함

2. 각 서비스 backend가 SSO 검증 후 notification-be용 내부 token을 만들어 전달
   - token payload에는 User_TM.UserId가 들어감
   - 브라우저가 아니라 backend에서만 생성

3. notification-be에 server-to-server 디바이스 등록 API 추가
   - backend가 검증한 User_TM.UserId와 registration_token을 body/header로 전달
   - 별도 server-to-server 인증 필요
```

현재 코드 기준으로는 `/v1/devices`가 cookie 기반 로그인 사용자에 의존한다.

SSO access_token을 notification-be가 그대로 이해할 수 있다면 1번이 가장 적은 변경이다.

다만 여러 서비스 backend가 안정적으로 붙는 운영 구조라면 3번처럼 server-to-server 등록 API를 별도로 두는 편이 책임 경계가 더 명확할 수 있다.

SSO와 공통 `User_TM` 기준에서는 핵심 규칙이 단순해진다.

```text
프론트는 user_id를 직접 보내지 않는다.
backend는 SSO로 현재 User_TM.UserId를 확정한다.
notification-be는 그 User_TM.UserId 기준으로 device token을 저장한다.
```

### 5.2 도메인 이벤트 발생 시점 결정

알림은 프론트 클릭만으로 보내면 안 된다.

backend에서 실제 DB 변경이 성공한 뒤에 보내야 한다.

예:

```text
댓글 작성 요청 수신
댓글 DB 저장 성공
트랜잭션 commit 성공
게시글 작성자에게 알림 필요 여부 판단
notification-be 발송 요청
```

이 순서가 중요한 이유:

```text
DB 저장 실패했는데 알림만 가는 문제 방지
권한 없는 요청으로 알림이 나가는 문제 방지
중복 요청으로 알림이 여러 번 나가는 문제 방지
```

### 5.3 발송 대상 결정

backend가 결정해야 하는 것:

```text
누구에게 보낼지, 즉 어떤 User_TM.UserId에 보낼지
어떤 이벤트에서 보낼지
어떤 template_code를 사용할지
중복 발송을 막을 기준은 무엇인지
사용자가 해당 알림을 꺼둔 경우 어떻게 처리할지
```

SSO와 공통 `User_TM` 전제에서는 발송 대상 변환이 필요 없다.

```text
서비스 backend에서 알고 있는 대상 UserId
  = User_TM.UserId
  = notification-be /v1/messages:sendUser의 user_id
```

단일 사용자 발송:

```http
POST /v1/messages:sendUser
Content-Type: application/json

{
  "user_id": "target-user-id",
  "template_code": "template-code",
  "data": {}
}
```

구독/정의 기반 발송:

```http
POST /v1/messages:sendDefinition
Content-Type: application/json

{
  "definition_code": "definition-code",
  "template_code": "template-code",
  "data": {}
}
```

현재 로컬 Coding_Quiz 테스트는 `sendUser`만 사용한다.

### 5.4 template_code 관리

backend는 어떤 이벤트가 어떤 template_code를 쓸지 알고 있어야 한다.

예:

```text
COMMENT_CREATED -> comment_created_ko
MESSAGE_RECEIVED -> message_received_ko
BID_APPROVED -> bid_approved_ko
QUIZ_BADGE_EARNED -> quiz_badge_earned_ko
```

현재 로컬 테스트 template:

```text
d6aa9a90-086e-464d-ba62-909dea8e2421
```

운영에서는 UUID를 코드로 직접 쓰는 것보다 사람이 읽을 수 있는 안정적인 code 정책을 정하는 것이 좋다.

예:

```text
coding_quiz_test_ko
comment_created_ko
message_received_ko
```

### 5.5 notification-be 장애 처리

notification-be 호출이 실패해도 원래 서비스 요청 전체를 실패시킬지 결정해야 한다.

일반적으로 권장:

```text
핵심 도메인 작업은 성공 처리
알림 발송 실패는 로그/재시도 큐로 분리
```

예:

```text
댓글 저장 성공
notification-be 발송 실패
사용자에게는 댓글 작성 성공 응답
서버 로그 또는 retry queue에 알림 실패 기록
```

단, 알림 발송 자체가 핵심 기능인 관리자 발송 화면에서는 실패를 사용자에게 보여줘야 한다.

## 6. notification-be가 담당하는 일

`tvcf-notification-be`의 책임:

```text
User_TM 유저 존재 확인
NotificationDevice_TM에 FCM token 저장
NotificationCategory_TM / NotificationDefinition_TM / NotificationTemplate_TM 관리
NotificationDevice_TM에서 대상 token 조회
Firebase Admin SDK로 FCM 발송
NotificationMessage_TM에 발송 결과 저장
```

현재 주요 API:

```text
POST /v1/devices
POST /v1/messages:sendUser
POST /v1/messages:sendDefinition
GET /v1/templates
POST /v1/categories
POST /v1/definitions
POST /v1/templates
```

현재 주의할 점:

```text
/v1/devices는 access_token cookie 기반
/v1/messages:sendUser는 현재 별도 인증 없이 호출 가능
Firebase Admin SDK env가 없으면 sendUser에서 500
NotificationMessage_TM 저장 commit은 현재 확인 완료
```

공통 `User_TM` 기준에서 추가로 볼 점:

```text
NotificationDevice_TM.UserId는 SSO의 User_TM.UserId와 같아야 함
여러 회사 프로젝트가 같은 사용자의 token을 등록할 때 중복/갱신 정책 확인 필요
현재 모델에는 UserId + DeviceFamily + BrowserFamily unique 제약이 있음
프로젝트별로 같은 브라우저/디바이스에서 token을 따로 등록해야 한다면 제약 조건 재검토 필요
```

## 7. FCM 설정 문서

Firebase Console에서 프로젝트와 키를 준비하는 절차는 이 문서에서 다루지 않는다.

참조:

```text
FCM_CONSOLE_SETUP.md
```

이 문서는 회사 프로젝트가 준비된 FCM 설정값을 받아서 `frontend -> backend -> notification-be` 흐름으로 연결하는 역할 분리만 다룬다.

## 8. 회사 프로젝트별 구현 체크리스트

### 8.1 Frontend 체크리스트

```text
FCM 설정값 env 반영
알림 권한 요청 UI 구현
FCM token 발급 구현
발급 token을 자기 backend로 전달
foreground onMessage 처리
token 재발급/재등록 처리
알림 수신 로그 또는 사용자 알림 UI 구현
```

### 8.2 Backend 체크리스트

```text
SSO로 현재 User_TM.UserId 식별
registration_token 등록 endpoint 구현
notification-be /v1/devices 호출 구현
도메인 이벤트별 알림 발송 조건 정의
발송 대상 User_TM.UserId 결정
이벤트별 template_code 매핑
notification-be /v1/messages:sendUser 또는 sendDefinition 호출 구현
notification-be 실패 시 로깅/재시도 정책 정의
중복 발송 방지 키 정의
token 등록 API idempotency 정책 정의
SSO token 전달 또는 운영 server-to-server 인증 방식 결정
```

### 8.3 notification-be 체크리스트

```text
SSO token 또는 내부 token에서 User_TM.UserId를 안정적으로 읽는지 확인
필요 category/definition/template 생성
서비스별 알림 구독 정책 정리
FCM 서버 발송 env 설정
운영 DB migration 적용
server-to-server 인증 정책 정리
발송 이력 저장 commit 유지
```

## 9. 권장 연동 형태

권장:

```text
frontend -> own backend -> notification-be
```

비권장:

```text
frontend -> notification-be 직접 호출
```

비권장 이유:

```text
브라우저에 서버 인증 정보를 둘 수 없음
서비스별 로그인 토큰과 notification-be 인증 정책이 섞임
user_id 위조 방지 책임이 불명확해짐
도메인 이벤트 성공 여부를 프론트가 확정할 수 없음
```

## 10. 현재 Coding_Quiz 테스트를 회사 프로젝트로 치환하면

현재:

```text
Coding_Quiz frontend
  /fcm-test 화면 버튼

Coding_Quiz backend
  /fcm-test/register-device
  /fcm-test/send

notification-be
  /v1/devices
  /v1/messages:sendUser
```

회사 프로젝트 적용:

```text
각 서비스 frontend
  알림 권한 요청
  FCM token 발급
  자기 backend에 token 등록 요청

각 서비스 backend
  SSO로 현재 User_TM.UserId 확인
  notification-be에 token 등록
  실제 업무 이벤트 발생 시 notification-be에 발송 요청

notification-be
  token 저장
  template 조회
  Firebase 발송
```

예를 들어 댓글 알림이라면:

```text
사용자 A가 댓글 작성
  -> frontend가 backend에 댓글 저장 요청
  -> backend가 댓글 저장
  -> backend가 게시글 작성자 User_TM.UserId 결정
  -> backend가 notification-be /v1/messages:sendUser 호출
  -> notification-be가 게시글 작성자의 device token으로 FCM 발송
  -> 게시글 작성자 브라우저가 알림 수신
```

예를 들어 Coding_Quiz 배지 알림이라면:

```text
사용자가 퀴즈 제출
  -> backend가 채점 결과 저장
  -> backend가 새 배지 획득 여부 판단
  -> backend가 notification-be /v1/messages:sendUser 호출
  -> notification-be가 해당 사용자의 FCM token으로 알림 발송
```

## 11. 다음에 결정해야 할 설계 이슈

운영 연동 전에 결정할 것:

```text
SSO access_token을 notification-be에 그대로 전달할지
backend가 SSO 검증 후 notification-be용 내부 token을 만들지
device token 등록 API를 cookie 기반으로 유지할지 server-to-server 방식으로 바꿀지
notification-be 발송 API 인증을 어떻게 걸지
template_code를 UUID로 쓸지 사람이 읽는 코드로 관리할지
발송 실패 재시도를 notification-be가 할지 각 서비스 backend가 할지
NotificationMessage_TM 저장 commit 흐름을 보장할지
사용자별 알림 수신 동의/구독 정책을 어디서 관리할지
```

## 12. 현재 상태 기준 결론

현재 로컬 테스트는 아래 단계까지는 완료된 상태다.

```text
로컬 DB 연결
notification-be schema 준비
테스트 user/template 준비
브라우저 FCM token 등록
Coding_Quiz backend 설정 반영
Firebase env를 명시한 sendUser 성공 응답
NotificationMessage_TM 발송 이력 저장 확인
```

아직 최종 확인해야 할 것:

```text
현재 실행 중인 notification-be를 Firebase env와 함께 다시 켠 상태에서
Coding_Quiz 화면 버튼으로 sendUser success_count=1 확인
브라우저 Foreground 수신 로그에 실제 메시지 표시 확인
```

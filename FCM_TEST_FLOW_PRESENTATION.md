# FCM 테스트 흐름 발표용 설명서

이 문서는 `Coding_Quiz`를 이용해 `tvcf-notification-be`의 FCM 발송 흐름을 설명할 때, 듣는 사람이 빠르게 이해할 수 있도록 만든 발표용 자료다.

기술 구현 세부사항보다 아래 질문에 답하는 것을 목표로 한다.

```text
왜 이 테스트를 하는가?
프론트는 무엇을 하는가?
백엔드는 무엇을 하는가?
notification-be는 무엇을 하는가?
각 버튼은 실제 서비스의 어떤 시점에 해당하는가?
성공 화면이 의미하는 것은 무엇인가?
```

## 1. 한 문장 요약

이 테스트는 `Coding_Quiz`가 직접 FCM을 발송하지 않고, `tvcf-notification-be`에 요청을 넘겼을 때 실제 Firebase FCM을 통해 브라우저가 메시지를 받을 수 있는지 확인하는 로컬 통합 테스트다.

```text
Coding_Quiz frontend
  -> Coding_Quiz backend
  -> tvcf-notification-be
  -> Firebase FCM
  -> Browser foreground 수신
```

## 2. 왜 Coding_Quiz로 테스트하는가

실제 회사 서비스마다 프론트와 백엔드가 따로 있다.

알림 구조도 보통 아래처럼 흘러간다.

```text
각 서비스 frontend
  -> 각 서비스 backend
  -> 공통 알림 서버 notification-be
  -> Firebase FCM
  -> 사용자 브라우저 또는 앱
```

`Coding_Quiz`는 실제 회사 서비스 대신 이 구조를 작게 재현하는 테스트 클라이언트 역할을 한다.

즉, `Coding_Quiz` 자체가 알림 서비스를 만드는 것이 아니다.

```text
Coding_Quiz frontend:
  브라우저 token 발급과 foreground 수신 확인

Coding_Quiz backend:
  notification-be로 token 등록/발송 요청 전달

tvcf-notification-be:
  DB 조회, Firebase Admin SDK 발송, 결과 저장
```

## 3. 전체 흐름

```text
1. 브라우저가 Firebase에서 FCM token을 발급받는다.
2. Coding_Quiz backend가 그 token을 notification-be에 등록한다.
3. 테스트 버튼이 실제 서비스 이벤트를 대신한다.
4. Coding_Quiz backend가 notification-be에 발송 요청을 보낸다.
5. notification-be가 DB에서 user/template/device token을 조회한다.
6. notification-be가 Firebase Admin SDK로 FCM을 보낸다.
7. 브라우저가 foreground 상태에서 메시지를 받는다.
8. /fcm-test 화면의 수신 로그에 payload가 표시된다.
```

그림으로 보면 아래와 같다.

```text
Browser
  |
  | FCM token 발급
  v
Coding_Quiz frontend
  |
  | token 등록 요청 / 발송 요청
  v
Coding_Quiz backend
  |
  | /v1/devices / /v1/messages:sendUser
  v
tvcf-notification-be
  |
  | User_TM / NotificationDevice_TM / NotificationTemplate_TM 조회
  v
notification DB
  |
  | Firebase Admin SDK
  v
Firebase FCM
  |
  | foreground message
  v
Browser
```

## 4. 역할 분리

| 구분 | 하는 일 | 하지 않는 일 |
| --- | --- | --- |
| Coding_Quiz frontend | FCM token 발급, 알림 권한 요청, foreground 메시지 표시 | Firebase Admin SDK 발송, 서버 인증 토큰 보관 |
| Coding_Quiz backend | 현재 테스트 요청을 notification-be로 전달 | FCM 직접 발송, NotificationDevice_TM 직접 저장 |
| tvcf-notification-be | token 저장, template 조회, FCM 발송, 발송 이력 저장 | 서비스별 비즈니스 이벤트 판단 |
| Firebase FCM | token 발급과 메시지 전달 | user/template 판단, 발송 이력 저장 |

가장 중요한 원칙은 아래다.

```text
프론트는 token을 만든다.
각 서비스 백엔드는 이벤트와 사용자를 확정한다.
notification-be는 token 저장과 실제 FCM 발송을 담당한다.
```

## 5. 화면 버튼별 의미

현재 테스트 화면에는 큰 단계가 4개 있다.

```text
1. FCM token 발급
2. Token 등록
3. CodingQuiz 백엔드로 발송 요청
4. Foreground 수신 로그
```

각 단계는 실제 서비스의 특정 시점을 수동으로 재현한 것이다.

## 6. 1단계: FCM token 발급

### 화면에서 하는 일

`FCM token 발급` 버튼을 누른다.

### 실제 동작

```text
브라우저
  -> 로그인 완료 상태 확인
  -> 사용자의 알림 설정 ON 여부 확인
  -> 알림 권한 요청 또는 확인
  -> Firebase Web SDK 초기화
  -> getToken() 호출
  -> FCM registration token 발급
```

### 실제 서비스에서는 언제 하는가

최초 발급 시점:

```text
로그인 완료
  -> 사용자가 알림 설정을 ON
  -> 브라우저 알림 권한 granted
  -> 그 직후 getToken()
```

이후 확인/갱신 시점:

```text
로그인 완료 후 앱 시작 시
알림 설정 화면 진입 시
사용자 알림 설정이 ON이고 Notification.permission이 granted일 때
token 변경 여부 확인이 필요할 때
```

### 이 단계가 성공했다는 의미

```text
브라우저 알림 권한이 허용됨
Firebase Web 설정이 맞음
VAPID key가 맞음
브라우저가 FCM 수신 대상이 될 수 있음
```

### 주의

이 단계는 아직 서버 DB에 아무것도 저장하지 않는다.

```text
token 발급 = 알림 받을 주소를 만드는 단계
```

백엔드가 이 token을 직접 발급할 수는 없다.

```text
백엔드는 "token 등록이 필요하다"는 신호를 줄 수 있음
실제 getToken()은 브라우저/앱에서만 가능
```

## 7. 2단계: Token 등록

### 화면에서 하는 일

`Token 등록` 버튼을 누른다.

### 실제 동작

```text
Coding_Quiz frontend
  -> Coding_Quiz backend /fcm-test/register-device
  -> Coding_Quiz backend가 로그인 JWT로 현재 user 확인
  -> user.username을 notification-be UserId로 사용
  -> notification-be용 임시 JWT { userId: username } 생성
  -> tvcf-notification-be /v1/devices
  -> NotificationDevice_TM에 token 저장
```

notification-be로 가는 요청은 개념적으로 아래와 같다.

```http
POST /v1/devices
Cookie: access_token=<Coding_Quiz backend가 만든 notification-be용 JWT>
Content-Type: application/json

{
  "registration_token": "<브라우저 FCM token>"
}
```

### 실제 서비스에서는 언제 하는가

```text
getToken()으로 token을 받은 직후
이전에 같은 user/env/token으로 등록 성공한 기록이 없을 때
로그인한 사용자의 token이 서버에 없을 때
브라우저/기기/token이 바뀌었을 때
사용자가 알림 권한을 다시 허용했을 때
```

### 이 단계가 성공했다는 의미

```text
notification-be가 이 유저의 브라우저 token을 알고 있음
나중에 user_id로 발송 요청하면 이 token을 찾을 수 있음
```

### 주의

Token 등록은 알림 발송이 아니다.

```text
token 등록 = user_id와 FCM token을 notification-be DB에 연결하는 단계
```

현재 테스트에서는 등록 대상 유저가 화면 입력값이나 env 값이 아니라 Coding_Quiz 로그인 유저의 `username`으로 결정된다.

```text
Coding_Quiz 로그인 user.username
  = notification-be User_TM.UserId
```

따라서 notification-be DB에는 같은 `UserId`가 있어야 하고, username은 notification-be 제약에 맞게 20자 이하여야 한다.

프론트에서 중복 등록 요청을 줄일 수는 있지만 완전히 막을 수는 없다. 그래서 서버 등록 API는 같은 token이 다시 들어와도 안전해야 한다.

```text
현재 로컬 테스트:
  같은 token이면 Device already exists가 나올 수 있음
  이미 등록된 상태로 보고 발송 단계로 진행 가능

운영 권장:
  같은 token 재등록은 성공으로 처리하거나 기존 device를 반환
  같은 user/device/browser이면 token을 최신 값으로 갱신
```

## 8. 3단계: CodingQuiz 백엔드로 발송 요청

### 화면에서 하는 일

`CodingQuiz 백엔드로 발송 요청` 버튼을 누른다.

### 실제 동작

```text
Coding_Quiz frontend
  -> Coding_Quiz backend /fcm-test/send

Coding_Quiz backend
  -> tvcf-notification-be /v1/messages:sendUser
```

notification-be로 가는 요청은 아래와 같다.

```http
POST /v1/messages:sendUser
Content-Type: application/json

{
  "user_id": "<Coding_Quiz 로그인 user.username>",
  "template_code": "d6aa9a90-086e-464d-ba62-909dea8e2421"
}
```

notification-be 내부에서는 아래 일이 일어난다.

```text
User_TM에서 user_id 확인
NotificationTemplate_TM에서 template_code 확인
NotificationDevice_TM에서 user_id의 FCM token 조회
Firebase Admin SDK로 FCM 발송
NotificationMessage_TM에 발송 결과 저장
```

### 실제 서비스에서는 언제 하는가

알림을 보내야 하는 비즈니스 이벤트가 확정된 뒤다.

예:

```text
댓글 저장 성공 후
새 메시지 저장 성공 후
입찰 상태 변경 성공 후
공지 발송 대상 확정 후
퀴즈 결과 저장 후 배지 획득이 확정된 후
```

중요한 순서는 아래다.

```text
서비스 DB 저장 성공
  -> 알림 대상 결정
  -> template_code 결정
  -> notification-be에 발송 요청
```

DB 저장이 실패했는데 알림만 가면 안 된다.

### 이 단계가 성공했다는 의미

```text
Coding_Quiz backend가 notification-be API 규칙대로 요청을 보냄
notification-be가 DB에서 user/template/device token을 찾음
Firebase FCM 발송 요청이 성공함
```

화면의 성공 문구:

```text
target 1, success 1, failure 0
```

의미:

```text
target 1:
  발송 대상 token을 1개 찾음

success 1:
  Firebase가 1개 token에 대해 성공 응답을 반환함

failure 0:
  실패한 token이 없음
```

## 9. 4단계: Foreground 수신 로그

### 화면에서 보는 것

`Foreground 수신 로그` 영역에 메시지가 표시된다.

예:

```text
foreground
CodingQuiz FCM Test
Test message from notification-be.
```

payload 예:

```json
{
  "data": {
    "title": "CodingQuiz FCM Test",
    "body": "Test message from notification-be."
  }
}
```

### 실제 동작

```text
Firebase FCM
  -> 브라우저
  -> Firebase Web SDK onMessage()
  -> /fcm-test 화면 로그 표시
```

### 실제 서비스에서는 무엇으로 바뀌는가

서비스 UI에 맞게 처리한다.

예:

```text
toast 표시
알림 카운터 증가
알림 목록 새로고침
채팅방 메시지 갱신
사용자 알림 메뉴에 새 항목 표시
```

### 주의

현재 테스트는 foreground만 확인한다.

```text
/fcm-test 페이지를 열어둔 상태에서 받는 메시지
```

background 알림창 표시는 현재 테스트 범위에서 제외한다.

## 10. 실제 서비스 이벤트와 테스트 버튼의 대응

| 테스트 화면 버튼 | 실제 서비스에서 대응되는 시점 |
| --- | --- |
| FCM token 발급 | 로그인 완료 후 사용자가 알림 ON을 하고 권한이 granted된 직후 |
| FCM token 확인/갱신 | 로그인 완료 후 앱 시작 시 또는 알림 설정 화면 진입 시 |
| Token 등록 | getToken() 직후, 이전 등록 token과 다르거나 등록 기록이 없을 때 |
| CodingQuiz 백엔드로 발송 요청 | 댓글/메시지/입찰/퀴즈 결과 같은 이벤트가 DB에 확정된 시점 |
| Foreground 수신 로그 | Firebase가 브라우저에 메시지를 전달한 시점 |

즉 테스트 화면의 발송 버튼은 실제 서비스 이벤트를 대신한다.

```text
실제 서비스:
  댓글 생성 완료 -> 알림 발송

현재 테스트:
  버튼 클릭 -> 알림 발송
```

## 11. 이 테스트가 증명하는 것

성공 화면이 나오면 아래를 증명한다.

```text
브라우저가 FCM token을 발급받을 수 있음
Coding_Quiz backend가 notification-be에 token 등록 요청을 보낼 수 있음
notification-be가 token을 DB에 저장할 수 있음
Coding_Quiz backend가 notification-be에 발송 요청을 보낼 수 있음
notification-be가 user/template/device token을 조회할 수 있음
notification-be가 Firebase Admin SDK로 실제 발송할 수 있음
브라우저가 foreground 상태에서 payload를 받을 수 있음
```

## 12. 이 테스트가 증명하지 않는 것

이 테스트는 아래를 검증하지 않는다.

```text
실제 회사 SSO 전체 로그인 흐름
운영 Firebase 프로젝트 설정
실제 댓글/입찰/메시지 도메인 이벤트
모바일 앱 push
background 알림창 표시
사용자별 알림 수신 동의 정책
운영 보안 정책
장애 재시도 정책
```

이 테스트는 "각 서비스 backend가 notification-be에 붙으면 실제 FCM까지 갈 수 있는가"를 보는 연결 테스트다.

## 13. 발표할 때 추천 설명 순서

### 13.1 먼저 큰 그림을 말한다

```text
이번 테스트는 Coding_Quiz가 알림을 직접 보내는 테스트가 아닙니다.
Coding_Quiz는 서비스 프로젝트 역할을 하고,
실제 발송은 공통 알림 서버인 notification-be가 담당합니다.
```

### 13.2 역할을 나눈다

```text
프론트는 token을 발급하고 메시지를 받습니다.
서비스 백엔드는 현재 사용자와 이벤트를 확정합니다.
notification-be는 token 저장과 Firebase 발송을 담당합니다.
```

### 13.3 화면 버튼을 실제 서비스 시점에 연결한다

```text
FCM token 발급은 로그인 후 사용자가 알림을 허용했을 때 브라우저가 알림 받을 주소를 만드는 단계입니다.
이후 앱 시작이나 알림 설정 화면에서는 같은 getToken()을 token 확인/갱신 용도로 사용합니다.
Token 등록은 이 브라우저 token을 현재 로그인 사용자와 연결해 서버에 저장하는 단계입니다.
발송 요청은 실제 서비스 이벤트가 발생한 상황을 버튼으로 대신한 것입니다.
Foreground 로그는 브라우저가 실제로 메시지를 받았다는 증거입니다.
```

### 13.4 성공 화면을 해석한다

```text
target 1은 대상 token을 찾았다는 뜻입니다.
success 1은 Firebase 발송이 성공했다는 뜻입니다.
foreground 로그는 브라우저가 payload를 실제로 받았다는 뜻입니다.
```

### 13.5 마지막으로 범위를 제한한다

```text
다만 이 테스트는 background 알림창이나 운영 SSO 전체 흐름까지 검증하는 것은 아닙니다.
현재는 foreground 수신과 notification-be 연동 흐름을 검증하는 단계입니다.
```

## 14. 발표용 짧은 스크립트

아래 문장을 그대로 읽어도 된다.

```text
이 화면은 Coding_Quiz가 FCM을 직접 보내는지 보는 테스트가 아닙니다.
실제 구조처럼 Coding_Quiz frontend가 브라우저 FCM token을 만들고,
Coding_Quiz backend가 그 token 등록과 발송 요청을 notification-be로 전달합니다.

notification-be는 자기 DB에서 user, template, device token을 조회한 뒤
Firebase Admin SDK를 이용해서 실제 FCM을 보냅니다.

첫 번째 버튼은 브라우저가 알림 받을 주소인 FCM token을 만드는 단계입니다.
실제 서비스에서는 로그인 완료 후 사용자가 알림을 켜고 권한을 허용한 직후 최초로 실행합니다.
이후에는 앱 시작이나 알림 설정 화면에서 token이 바뀌었는지 확인하는 용도로 실행합니다.

두 번째 버튼은 그 token을 현재 로그인 사용자와 연결해 notification-be의 디바이스 테이블에 저장하는 단계입니다.
중복 등록 요청은 프론트에서 줄이되, 서버는 같은 token이 다시 와도 안전하게 처리해야 합니다.
세 번째 버튼은 실제 서비스 이벤트가 발생했다고 가정하고 발송 요청을 보내는 단계입니다.
마지막 수신 로그는 Firebase가 브라우저에 payload를 실제로 전달했다는 증거입니다.

따라서 이 테스트가 성공했다는 것은
각 서비스 백엔드가 notification-be API 규칙대로 붙으면
실제 Firebase FCM까지 발송할 수 있다는 것을 의미합니다.
```

## 15. 한 장 요약

```text
목적:
  서비스 backend -> notification-be -> Firebase FCM 연동 검증

프론트:
  FCM token 발급
  foreground payload 수신

서비스 백엔드:
  token 등록 요청 전달
  비즈니스 이벤트 후 발송 요청 전달

notification-be:
  token 저장
  user/template/device 조회
  Firebase Admin SDK 발송
  발송 이력 저장

성공 기준:
  target_count=1
  success_count=1
  failure_count=0
  Foreground 수신 로그에 title/body 표시

테스트 범위 제외:
  background 알림
  모바일 push
  운영 SSO 전체 흐름
  실제 도메인 이벤트 정책
```

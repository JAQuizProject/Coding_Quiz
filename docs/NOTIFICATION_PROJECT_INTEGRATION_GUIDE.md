# Notification Project Integration Guide

이 문서는 실제 서비스 프로젝트가 `tvcf-notification-be`에 붙을 때의 역할 분리를 요약한다.

`Coding_Quiz`는 이 구조를 확인하기 위한 테스트 클라이언트다.
운영 알림 정책을 `Coding_Quiz` 안에 구현하는 것이 목적이 아니다.

## 전체 구조

권장 흐름:

```text
Service frontend
  -> Service backend
  -> tvcf-notification-be
  -> Firebase FCM
  -> Browser / App
```

프론트가 notification-be를 직접 호출하지 않는다.

## 사용자 기준

회사 서비스가 같은 사용자 테이블을 공유한다는 전제에서는 notification-be 기준 사용자도 `User_TM.UserId`다.

```text
서비스 로그인 사용자
  -> 서비스 backend에서 User_TM.UserId 확정
  -> notification-be에 같은 UserId 기준으로 token 등록/발송 요청
```

## Frontend 역할

프론트는 알림을 받을 준비만 한다.

```text
Firebase Web SDK 초기화
브라우저 알림 권한 요청
FCM registration token 발급
발급 token을 자기 backend로 전달
foreground 수신 처리
```

프론트가 보내는 값:

```json
{
  "registration_token": "<browser fcm token>"
}
```

프론트가 직접 결정하지 않는 값:

```text
user_id
server-to-server 인증값
Firebase service account
```

즉 프론트는 "누구에게 보낼지"를 판단하지 않는다.
프론트는 현재 브라우저가 받을 수 있는 token만 backend로 넘긴다.

## Backend 역할

서비스 backend는 현재 사용자와 알림 이벤트를 확정한다.

```text
현재 로그인 User_TM.UserId 확인
frontend가 준 registration_token을 notification-be에 등록
서비스 이벤트 발생 후 발송 대상 UserId 결정
template_code 결정
notification-be /v1/messages:sendUser 호출
```

backend가 확정하는 값:

| 값 | 의미 |
| --- | --- |
| 현재 UserId | token 등록 대상 또는 발송 대상 |
| registration_token | frontend가 넘긴 브라우저 token |
| template_code | 어떤 문구로 보낼지 정하는 코드 |
| 발송 시점 | 서비스 DB 작업이 성공한 뒤 |

token 등록 개념:

```text
POST /v1/devices
Cookie 또는 server-to-server 인증으로 현재 UserId 전달
body: { registration_token }
```

단일 사용자 발송:

```http
POST /v1/messages:sendUser
Content-Type: application/json

{
  "user_id": "<target User_TM.UserId>",
  "template_code": "<template code>"
}
```

## notification-be 역할

notification-be는 알림 발송 서버다.

```text
User_TM 확인
NotificationDevice_TM에 token 저장
NotificationTemplate_TM 조회
대상 UserId의 device token 조회
Firebase Admin SDK로 FCM 발송
NotificationMessage_TM에 결과 저장
```

## Coding_Quiz 테스트와 실제 서비스의 차이

현재 테스트:

```text
Coding_Quiz frontend
  -> /fcm-test 화면에서 token 발급/수신 확인

Coding_Quiz backend
  -> 로그인 username을 User_TM.UserId처럼 사용
  -> notification-be에 token 등록/발송 요청
```

실제 서비스:

```text
서비스 frontend
  -> 서비스 UI에서 token 발급/수신 처리

서비스 backend
  -> SSO/session으로 현재 User_TM.UserId 확정
  -> 실제 업무 이벤트 이후 notification-be에 발송 요청
```

예시:

```text
댓글 저장 성공
  -> 댓글 대상 사용자 UserId 결정
  -> 댓글 알림 template_code 선택
  -> notification-be /v1/messages:sendUser 호출
```

## 구현 체크리스트

Frontend:

```text
Firebase config env 반영
VAPID key env 반영
알림 권한 요청 UI
getToken() 처리
foreground onMessage() 처리
token을 자기 backend로 전달
```

Backend:

```text
현재 User_TM.UserId 확인
token 등록 endpoint 구현
notification-be /v1/devices 호출
이벤트별 template_code 관리
notification-be /v1/messages:sendUser 호출
notification-be 호출 실패 로그 처리
```

notification-be:

```text
Firebase Admin SDK env 설정
필요 template 준비
device token 저장 정책 확정
발송 이력 저장 확인
```

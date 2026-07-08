# Notification Project Integration Guide

이 문서는 실제 서비스 프로젝트가 `tvcf-notification-be`를 사용할 때의 역할 분리를 요약한다.

`Coding_Quiz`는 이 구조를 검증하기 위한 테스트 클라이언트다.

## 기본 구조

```text
Service frontend
  -> Service backend
  -> tvcf-notification-be
  -> Firebase FCM
  -> Browser / App
```

프론트가 notification-be를 직접 호출하지 않는다.
서비스 backend가 현재 사용자와 발송 이벤트를 확정한 뒤 notification-be를 호출한다.

## Frontend 역할

프론트는 알림을 받을 준비만 한다.

```text
로그인 상태 확인
사용자 알림 동의 확인
브라우저 알림 권한 요청
Firebase getToken()으로 FCM token 발급
자기 서비스 backend로 token 전달
foreground onMessage() 수신 처리
```

token 발급 권장 시점:

```text
최초: 로그인 후 사용자가 알림 수신을 허용한 직후
이후: 앱 시작 또는 알림 설정 화면 진입 시, 권한이 granted이고 알림 설정이 ON일 때
```

프론트가 직접 정하지 않는 값:

- notification-be `UserId`
- server-to-server 인증값
- 발송 대상
- template code
- Firebase service account

## Backend 역할

서비스 backend는 현재 사용자와 알림 이벤트를 확정한다.

```text
현재 로그인 사용자 확인
notification-be UserId 확정
frontend가 준 FCM token 등록
필요하면 definition 구독 등록
서비스 이벤트 성공 후 발송 요청
notification-be 오류 로그 처리
```

주요 호출:

```text
POST /v1/devices
POST /v1/subscriptions
POST /v1/messages:sendUser
POST /v1/messages:sendDefinition
```

## notification-be 역할

notification-be는 알림 저장/발송 서버다.

```text
User_TM 확인
NotificationDevice_TM에 token 저장
NotificationSubscription_TM에 구독 저장
NotificationTemplate_TM 조회
대상 device token 조회
Firebase Admin SDK로 FCM 발송
NotificationMessage_TM에 결과 저장
```

## Coding_Quiz 테스트와 실제 서비스 차이

Coding_Quiz 테스트:

```text
Coding_Quiz 로그인 username을 notification-be UserId처럼 사용
/fcm-test 화면에서 token 등록, 구독 등록, 발송 요청을 수동 실행
```

실제 서비스:

```text
서비스의 실제 로그인/권한/업무 이벤트 기준으로 UserId와 발송 시점을 결정
서비스 backend에서 notification-be 호출
```

예:

```text
댓글 저장 성공
  -> 댓글 대상 사용자 결정
  -> 댓글 알림 template_code 선택
  -> notification-be /v1/messages:sendUser 호출
```

## 구현 체크리스트

Frontend:

- Firebase Web SDK 설정
- VAPID key 설정
- 알림 권한 요청 UI
- `getToken()` 처리
- foreground `onMessage()` 처리
- token을 자기 backend로 전달

Backend:

- 현재 사용자와 notification-be `UserId` 매핑
- token 등록 API
- 구독 등록 API가 필요한지 판단
- 이벤트별 template/definition code 관리
- notification-be 호출 실패 로그

notification-be:

- Firebase Admin SDK credential 설정
- template/definition seed
- device token 등록 정책
- subscription 등록 정책
- 발송 이력 저장 정책

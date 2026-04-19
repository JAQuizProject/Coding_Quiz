# FCM 테스트 흐름 발표용 요약

이 문서는 `Coding_Quiz`를 이용한 알림 서버 테스트를 짧게 설명하기 위한 발표용 자료다.

## 한 문장 요약

`Coding_Quiz`는 알림을 직접 보내지 않고, 실제 서비스 프로젝트처럼 `tvcf-notification-be`에 token 등록과 발송 요청을 보내서 Firebase FCM 수신까지 확인한다.

```text
Coding_Quiz frontend
  -> Coding_Quiz backend
  -> tvcf-notification-be
  -> Firebase FCM
  -> Browser foreground
```

## 왜 Coding_Quiz로 테스트하는가

실제 서비스 연동 구조를 작게 재현하기 위해서다.

```text
서비스 frontend
  -> 서비스 backend
  -> notification-be
  -> Firebase FCM
```

`Coding_Quiz`는 여기서 서비스 frontend/backend 역할만 맡는다.

## 역할

| 구분 | 역할 |
| --- | --- |
| Coding_Quiz frontend | FCM token 발급, foreground 수신 로그 표시 |
| Coding_Quiz backend | 로그인 유저 기준으로 notification-be 요청 전달 |
| tvcf-notification-be | token 저장, template 조회, Firebase FCM 발송 |
| Firebase FCM | 브라우저로 메시지 전달 |

## 화면 버튼 의미

| 버튼 | 의미 |
| --- | --- |
| FCM token 발급 | 브라우저가 FCM 수신 주소를 받음 |
| Token 등록 | 현재 로그인 유저와 FCM token을 notification-be DB에 연결 |
| CodingQuiz 백엔드로 발송 요청 | 실제 서비스 이벤트 대신 발송 요청을 수동 실행 |
| Foreground 수신 로그 | 브라우저가 FCM payload를 받은 결과 |

버튼을 실제 서비스 시점으로 바꾸면 이렇게 볼 수 있다.

```text
FCM token 발급
  -> 로그인 후 사용자가 알림 허용

Token 등록
  -> 이 브라우저 token을 현재 사용자에게 연결

발송 요청
  -> 댓글/메시지/상태 변경 같은 이벤트가 확정됨

Foreground 수신 로그
  -> 브라우저가 Firebase payload를 받음
```

## 사용자 기준

현재 테스트에서는 화면에서 User ID를 입력하지 않는다.

```text
Coding_Quiz 로그인 username
= notification-be User_TM.UserId
= sendUser user_id
```

## 성공 화면의 의미

```text
target_count = 1
  notification-be가 발송 대상 token을 1개 찾음

success_count = 1
  Firebase가 해당 token 발송을 성공 처리함

Foreground 수신 로그 표시
  브라우저가 payload를 실제로 받음
```

성공 화면을 설명할 때는 아래처럼 말하면 된다.

```text
target_count는 알림 서버가 DB에서 찾은 대상 token 수입니다.
success_count는 Firebase가 발송 요청을 받아 성공 처리한 수입니다.
foreground 로그는 브라우저가 payload를 실제로 받은 화면 증거입니다.
```

## 테스트 범위

확인하는 것:

```text
브라우저 FCM token 발급
Coding_Quiz backend -> notification-be 요청
notification-be -> Firebase FCM 발송
브라우저 foreground 수신
```

확인하지 않는 것:

```text
background 알림창
모바일 push
운영 SSO 전체 흐름
실제 서비스 도메인 이벤트
```

## 발표용 짧은 설명

```text
이 화면은 Coding_Quiz가 FCM을 직접 보내는 테스트가 아닙니다.
Coding_Quiz는 서비스 프로젝트 역할을 하고,
실제 발송은 공통 알림 서버인 notification-be가 담당합니다.

프론트는 FCM token을 발급하고,
백엔드는 로그인 유저 기준으로 notification-be에 token 등록과 발송 요청을 전달합니다.
notification-be는 DB에서 user/template/device token을 조회한 뒤 Firebase Admin SDK로 FCM을 보냅니다.

성공 기준은 target 1, success 1, failure 0이고,
마지막으로 foreground 수신 로그에 title/body가 표시되는 것입니다.
```

## 한 장 요약

```text
목적:
  서비스 backend -> notification-be -> Firebase FCM 연결 확인

핵심 기준:
  Coding_Quiz 로그인 username = notification-be User_TM.UserId

성공 기준:
  target 1 / success 1 / failure 0
  foreground 로그 표시

범위:
  foreground 수신 테스트
  background, 모바일 push, 운영 SSO는 제외
```

# notification-be 회의 메모

이 문서는 `Coding_Quiz`로 알림 서버를 테스트하면서 확인한 notification-be 쪽 논의 안건만 요약한다.

`Coding_Quiz` 자체 요구사항이 아니라, 알림 서버가 실제 서비스 프로젝트들과 안정적으로 연동되기 위해 확인해야 할 내용이다.

## 전제

```text
notification-be 사용자 기준 = User_TM.UserId
Coding_Quiz 테스트 사용자 기준 = 로그인 username
```

## 논의 안건

### 1. FCM token 등록은 idempotent해야 함

현재 확인된 동작:

```text
같은 token 재등록
-> 400 Device already exists
```

논의 방향:

```text
같은 token이면 에러가 아니라 기존 device 반환 또는 갱신
같은 user/browser에서 token이 바뀌면 기존 row update
새 로그인 사용자가 같은 token을 등록하면 현재 UserId 기준으로 소유권 갱신 검토
```

결정해야 할 것:

```text
같은 token이 들어왔을 때 기존 row 반환인지 update인지
다른 UserId에 있던 token을 현재 UserId로 옮길지
응답 status를 200으로 할지 201로 유지할지
```

### 2. User-Agent 전달과 device/browser 식별

현재 테스트에서는 서비스 backend가 원본 브라우저 `User-Agent`를 notification-be로 전달한다.

논의 방향:

```text
User-Agent가 비어 있을 때 저장 정책 확정
DeviceFamily / BrowserFamily 파싱 실패 시 기본값 정책 확정
UserId + DeviceFamily + BrowserFamily unique 제약과 token 갱신 정책 정리
```

결정해야 할 것:

```text
User-Agent가 없을 때 허용할지
unknown 값으로 저장할지
원본 User-Agent를 별도 컬럼으로 남길지
```

### 3. Firebase Admin SDK 설정 검증

notification-be가 실제 FCM을 보내려면 Firebase Admin SDK credential이 필요하다.

논의 방향:

```text
GOOGLE_APPLICATION_CREDENTIALS 주입 방식 정리
GOOGLE_CLOUD_PROJECT 설정 방식 정리
서버 시작 또는 발송 전 설정 누락을 명확히 감지
```

결정해야 할 것:

```text
로컬/개발/운영별 credential 주입 방식
서버 시작 시 설정 검증 여부
설정 누락 시 응답 메시지 형식
```

### 4. 응답 코드와 에러 형태 정리

서비스 backend가 notification-be를 호출하려면 실패 응답 기준이 명확해야 한다.

논의 방향:

```text
중복 token
User_TM에 UserId 없음
template_code 없음
Firebase 설정 누락
예상하지 못한 DB 오류
```

각 케이스의 HTTP status와 response body 형태를 정해야 한다.

## 결론

현재 테스트의 핵심 발견은 `/v1/devices`가 단순 insert API처럼 동작한다는 점이다.
실제 서비스 연동에서는 token 등록이 반복될 수 있으므로, device 등록 API는 upsert 성격으로 정리되는 것이 좋다.

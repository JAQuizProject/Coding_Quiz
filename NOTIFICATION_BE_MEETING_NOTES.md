# notification-be 회의 메모

## 전제

notification-be는 현재 `User_TM.UserId`를 사용자 식별자로 사용한다.
이 부분은 논의 대상이 아니라 이미 코드 기준으로 정해진 계약이다.

Coding_Quiz 쪽 테스트는 이 계약에 맞춰 로그인 유저의 `username`을 `User_TM.UserId`로 매핑하도록 정리했다.

## 내일 이야기할 실제 문제와 대책

### 1. 같은 FCM token 재등록 시 400 발생

확인된 현상:

```text
POST /v1/devices
같은 registration_token 재등록
-> 400 Device already exists
```

왜 문제인지:

실제 서비스에서는 사용자가 로그인하거나 페이지를 다시 열 때 FCM token 등록 요청이 반복될 수 있다.
이미 등록된 token을 다시 보냈다는 이유로 에러가 나면 각 프로젝트의 프론트/백엔드가 불필요한 예외 처리를 해야 한다.

대책:

```text
같은 token이면 에러로 보지 않고 기존 device를 반환한다.
필요하면 last_used_at만 갱신한다.
응답은 200 OK로 맞춘다.
```

### 2. token 변경 시 UNIQUE 제약으로 500 발생 가능

확인된 현상:

```text
UNIQUE KEY 제약 조건 위반
UQ_NotificationDevice_TM_UserId_DeviceFamily_BrowserFamily
중복 키 값: (<Coding_Quiz 로그인 username>, , )
```

왜 문제인지:

FCM token은 브라우저 상태, 권한 재설정, 서비스워커 상태에 따라 바뀔 수 있다.
같은 사용자와 같은 브라우저/디바이스 조합에서 새 token이 들어오면 새 row insert가 아니라 기존 row update가 맞다.

대책:

```text
UserId + DeviceFamily + BrowserFamily가 이미 있으면 insert하지 않는다.
기존 row의 Token, LastUsedAt을 update한다.
UNIQUE 제약 위반이 사용자에게 500으로 노출되지 않게 한다.
```

### 3. User-Agent가 비면 브라우저/디바이스 구분이 무너짐

확인된 현상:

```text
중복 키 값: (<Coding_Quiz 로그인 username>, , )
```

뒤의 두 값이 비어 있으므로 `DeviceFamily`, `BrowserFamily`가 빈 값으로 저장된 상태다.

왜 문제인지:

각 프로젝트 backend가 notification-be로 실제 브라우저 `User-Agent`를 전달하지 않으면 Chrome, Edge, Safari 같은 구분이 제대로 되지 않는다.
그러면 서로 다른 브라우저 테스트도 같은 `(UserId, "", "")` 조합으로 충돌할 수 있다.

대책:

```text
각 프로젝트 backend는 /v1/devices 호출 시 원본 브라우저 User-Agent를 전달한다.
notification-be는 User-Agent 파싱 실패 시 빈 문자열 저장 정책을 유지할지, unknown 값으로 정규화할지 결정한다.
빈 User-Agent로 들어온 요청을 허용할지 400으로 막을지도 정한다.
```

### 4. Firebase Admin SDK 설정 누락 시 sendUser가 500으로 터짐

확인된 현상:

```text
POST /v1/messages:sendUser
Firebase credential/env가 없으면 500 Internal Server Error
```

왜 문제인지:

foreground 수신 테스트여도 실제 FCM 발송 주체는 notification-be다.
따라서 Firebase Admin SDK credential은 notification-be 실행 환경에 반드시 있어야 한다.

대책:

```text
notification-be 로컬/개발/운영 환경별 Firebase credential 주입 방식을 정한다.
서버 시작 시 credential 설정 여부를 검증한다.
설정이 없을 때 발송 시점 500보다 명확한 설정 오류로 드러나게 한다.
```

### 5. 실패 케이스의 응답 코드가 정리되어야 함

확인된 현상:

테스트 중 다음 실패들이 섞여서 나타났다.

```text
User not found
Device already exists
UNIQUE 제약 위반
Firebase credential 없음
template 없음 또는 잘못된 template_code
```

왜 문제인지:

각 프로젝트가 notification-be를 호출할 때 어떤 에러를 재시도해야 하는지, 어떤 에러를 사용자/운영 설정 문제로 봐야 하는지 구분하기 어렵다.

대책:

```text
이미 등록된 token: 200
같은 사용자/브라우저의 token 갱신: 200
다른 사용자/디바이스 token 충돌: 409
User_TM에 UserId 없음: 404
template_code 없음: 404
Firebase credential 없음: 서버 설정 오류
예상하지 못한 DB 오류: 500
```

### 6. 로컬/CI 테스트 환경 안정성

확인된 현상:

```text
Docker named pipe access denied
MSSQL testcontainer deadlock
```

왜 문제인지:

notification-be의 e2e 테스트가 Docker/MSSQL testcontainer에 의존한다.
개발자 PC 권한이나 Docker 상태에 따라 테스트 결과가 코드 문제와 섞여 보일 수 있다.

대책:

```text
Docker Desktop 실행/권한 조건을 문서화한다.
MSSQL testcontainer 초기화 실패와 deadlock에 대한 retry 정책을 점검한다.
로컬 DB 직접 연결 테스트와 testcontainer 테스트를 구분한다.
```

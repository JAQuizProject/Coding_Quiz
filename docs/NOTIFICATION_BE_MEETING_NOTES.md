# notification-be 회의 메모

이 문서는 `Coding_Quiz` 테스트 중 확인한 notification-be 쪽 논의 안건만 정리한다.

Coding_Quiz 기능 요구사항이 아니라, notification-be를 실제 서비스들과 안정적으로 연동하기 위해 확인할 내용이다.

## 1. Device token 재등록 정책

현재 확인된 동작:

```text
같은 token 재등록
-> 400 Device already exists
```

논의할 내용:

- 같은 token 재등록을 성공으로 볼지
- 기존 device row를 반환할지, 갱신할지
- 같은 브라우저 token이 다른 UserId로 들어오면 소유권을 옮길지
- `State=0`인 device가 있을 때 재등록을 어떻게 처리할지

실제 서비스에서는 로그인, 새로고침, 앱 재접속으로 token 등록 요청이 반복될 수 있다.
따라서 `/v1/devices`는 단순 insert보다 upsert 성격이 필요하다.

## 2. Device / Browser 식별

확인한 내용:

```text
User-Agent가 전달되면 BrowserFamily가 Chrome 등으로 저장된다.
User-Agent가 없거나 파싱 실패하면 빈 값이 저장될 수 있다.
```

논의할 내용:

- User-Agent가 없을 때 허용할지
- unknown 값으로 저장할지
- 원본 User-Agent를 별도 저장할지
- `UserId + DeviceFamily + BrowserFamily` 기준으로 token 갱신을 할지

## 3. LastUsedAt 갱신 시점

현재 테스트 관점에서는 `LastUsedAt`이 명확한 사용 시점으로 갱신되지 않는다.

논의할 내용:

- token 등록 성공 시 갱신할지
- FCM 발송 성공 시 갱신할지
- foreground 수신 ack가 생긴 뒤 갱신할지

현재 구조에서는 수신 ack가 없으므로 발송 성공 또는 token 등록 성공 기준이 현실적이다.

## 4. Subscription 재등록 정책

구독 기반 발송을 쓰려면 `NotificationSubscription_TM`이 필요하다.

논의할 내용:

- 같은 `UserId + DefinitionId` 재등록을 성공으로 볼지
- 기존 subscription을 반환할지
- 해지/재구독 상태값이 필요한지

device token과 마찬가지로 구독 등록도 반복 호출에 안전한 편이 좋다.

## 5. Firebase 설정 오류

확인한 오류:

```text
Project ID is required to access Cloud Messaging service.
```

원인:

```text
GOOGLE_APPLICATION_CREDENTIALS 또는 GOOGLE_CLOUD_PROJECT 설정 누락
```

논의할 내용:

- 서버 시작 시 Firebase 설정을 검증할지
- 발송 시점에만 검증할지
- 설정 누락 응답을 500 대신 명확한 에러 body로 줄지

## 정리

현재 가장 중요한 논의는 두 가지다.

1. `/v1/devices`와 `/v1/subscriptions`를 반복 호출에 안전하게 만들지
2. Firebase credential 누락처럼 운영자가 바로 이해해야 하는 오류를 명확한 응답으로 줄지

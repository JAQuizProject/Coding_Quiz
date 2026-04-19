# FCM Console Setup Guide

이 문서는 Firebase Console에서 FCM 테스트와 회사 프로젝트 연동을 위해 무엇을 설정해야 하는지 정리한다.

기존 테스트 문서와 프로젝트 연동 문서는 실행 흐름만 다루고, Firebase Console에서 키를 만들고 프로젝트를 관리하는 절차는 이 문서에서만 관리한다.

현재 수신 검증 범위는 foreground 수신이다.

```text
브라우저에서 페이지를 열어둠
  -> Firebase Web SDK onMessage()로 payload 수신
  -> 화면 로그, toast, 카운터, 알림 목록 갱신 등으로 처리
```

## 1. 전체 원칙

FCM 설정은 세 군데로 나뉜다.

```text
Frontend
  Firebase Web app config
  VAPID public key

Service backend
  notification-be 호출 주소
  notification-be 호출 인증값

notification-be
  Firebase Admin SDK service account JSON
  GOOGLE_APPLICATION_CREDENTIALS
  GOOGLE_CLOUD_PROJECT
```

중요한 규칙:

```text
Frontend의 Firebase projectId
Frontend의 VAPID key가 속한 Firebase project
notification-be의 service account JSON project_id
notification-be의 GOOGLE_CLOUD_PROJECT
```

위 값들은 같은 Firebase 프로젝트를 바라봐야 한다.

서로 다른 프로젝트 값이 섞이면 브라우저 token은 A 프로젝트에서 발급됐는데 서버는 B 프로젝트로 발송하는 상태가 된다. 이 경우 token 발급, token 등록, 발송 중 어느 단계에서든 실패할 수 있다.

## 2. 여러 회사 프로젝트 관리 기준

회사 프로젝트는 SSO를 사용하고, 각 서비스가 같은 `User_TM`을 바라본다는 전제다.

따라서 알림 서버 기준 사용자 ID는 각 서비스별 별도 ID가 아니라 공통 `User_TM.UserId`다.

권장 구조:

```text
회사 공통 Firebase project 1개
  -> 서비스별 Web app 여러 개 등록
  -> notification-be는 같은 Firebase project의 Admin SDK로 발송
```

예:

```text
Firebase project:
company-fcm-prod

Web apps:
tvcf-web-prod
admarket-web-prod
coding-quiz-test

notification-be:
company-fcm-prod service account 사용
```

이 방식이 단순한 이유:

```text
공통 User_TM.UserId 기준으로 device token을 저장할 수 있음
서비스별 frontend는 자기 Web app config만 사용하면 됨
notification-be는 하나의 Firebase Admin SDK 설정으로 발송 가능
프로젝트별 token과 service account가 섞일 위험이 줄어듦
```

Firebase 프로젝트를 여러 개로 나눠야 하는 경우도 있다.

```text
운영/스테이징을 강하게 분리해야 함
고객사별로 완전히 분리해야 함
보안/권한/과금/로그 소유권을 분리해야 함
```

그 경우에는 notification-be도 프로젝트별 발송 라우팅을 알아야 한다.

```text
service_type 또는 project_code
  -> Firebase project 선택
  -> 해당 project의 service account 선택
  -> 해당 project에서 발급된 token으로 발송
```

현재 코드 흐름처럼 단일 Firebase Admin SDK 설정으로 시작하는 구조에서는 여러 Firebase 프로젝트를 동시에 섞는 방식은 권장하지 않는다.

## 3. Firebase 프로젝트 만들기 또는 선택

Firebase Console:

```text
https://console.firebase.google.com
```

진입:

```text
Firebase Console
  -> 기존 프로젝트 선택
```

또는 새 테스트 프로젝트를 만든다.

```text
Firebase Console
  -> 프로젝트 추가
  -> 프로젝트 이름 입력
  -> Google Analytics는 테스트 목적이면 나중에 설정 가능
  -> 프로젝트 생성
```

현재 로컬 테스트 예시:

```text
Firebase project:
coding-quiz-fcm-test
```

회사에서는 개인 테스트 프로젝트가 아니라 회사 공통 Firebase 프로젝트를 기준으로 값들을 발급해야 한다.

## 4. Web app 등록

목적:

```text
각 frontend가 Firebase Web SDK를 초기화할 수 있게 Web app config를 발급받는다.
```

진입:

```text
Firebase Console
  -> 프로젝트 선택
  -> Project overview
  -> 앱 추가
  -> Web
```

이미 앱이 있으면:

```text
Firebase Console
  -> Project settings
  -> General
  -> Your apps
  -> Web app 선택 또는 Add app
```

입력:

```text
App nickname:
서비스와 환경을 알아볼 수 있는 이름
```

예:

```text
tvcf-web-local
tvcf-web-dev
tvcf-web-prod
admarket-web-dev
coding-quiz-local-test
```

현재 테스트에서는 Firebase Hosting 설정은 필수가 아니다.

등록 후 `SDK setup and configuration`의 `Config` 값을 frontend 환경변수로 옮긴다.

예:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...
```

이 값들은 브라우저에 들어가는 public config다. 비밀키가 아니다.

다만 public config라고 해서 아무 프로젝트 값이나 섞어도 된다는 뜻은 아니다. 이 값의 `projectId`는 VAPID key와 notification-be service account의 프로젝트와 맞아야 한다.

## 5. VAPID public key 생성

목적:

```text
브라우저에서 FCM registration token을 발급받을 때 사용하는 Web Push public key를 준비한다.
```

진입:

```text
Firebase Console
  -> 프로젝트 선택
  -> Project settings
  -> Cloud Messaging
  -> Web configuration
  -> Web Push certificates
  -> Generate key pair
```

생성 후 public key를 frontend 환경변수에 넣는다.

```env
NEXT_PUBLIC_FIREBASE_VAPID_KEY=...
```

사용 위치:

```text
frontend Firebase Web SDK getToken() 호출
```

개념:

```text
getToken(messaging, { vapidKey })
  -> 브라우저 FCM registration token 발급
```

VAPID private key를 직접 코드에 넣는 작업은 현재 구조에서 하지 않는다. Firebase Console이 key pair를 관리하고, frontend에는 public key만 들어간다.

## 6. Service account private key 생성

목적:

```text
notification-be가 Firebase Admin SDK로 FCM을 발송할 수 있게 서버 인증 정보를 준비한다.
```

진입:

```text
Firebase Console
  -> 프로젝트 선택
  -> Project settings
  -> Service accounts
  -> Firebase Admin SDK
  -> Generate new private key
```

다운로드되는 JSON은 서버 비밀키다.

주의:

```text
Git에 커밋하지 않는다.
frontend에 넣지 않는다.
각 서비스 backend에도 넣지 않는다.
notification-be 실행 환경 또는 배포 secret에만 둔다.
```

로컬 테스트 예시:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="C:/Users/gram/Desktop/coding-quiz-fcm-test-firebase-adminsdk-fbsvc-c193426100.json"
export GOOGLE_CLOUD_PROJECT="coding-quiz-fcm-test"
```

운영 환경에서는 로컬 파일 경로가 아니라 서버의 secret 관리 방식에 맞춰 넣어야 한다.

예:

```text
Windows 서비스 환경변수
Docker secret
Kubernetes secret
CI/CD secret
Cloud Run/App Hosting 환경변수
```

## 7. 각 프로젝트에 전달할 값

### 7.1 Frontend에 전달할 값

```env
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...
NEXT_PUBLIC_FIREBASE_VAPID_KEY=...
```

frontend가 하는 일:

```text
Firebase Web SDK 초기화
로그인 완료 후 사용자의 알림 설정 ON 여부 확인
사용자 동의 UI 이후 브라우저 알림 권한 요청
권한 granted 직후 FCM registration token 최초 발급
앱 시작 또는 알림 설정 화면에서 token 확인/갱신
발급 token을 자기 서비스 backend로 전달
foreground onMessage() 수신 처리
```

frontend가 가지면 안 되는 값:

```text
Firebase service account JSON
notification-be server-to-server secret
다른 사용자의 UserId
```

### 7.2 각 서비스 backend에 전달할 값

```env
TVCF_NOTIFICATION_BASE_URL=...
TVCF_NOTIFICATION_DEVICE_PATH=/v1/devices
TVCF_NOTIFICATION_SEND_USER_PATH=/v1/messages:sendUser
TVCF_NOTIFICATION_AUTH_TOKEN=...
```

backend가 하는 일:

```text
SSO로 현재 User_TM.UserId 확인
frontend가 준 registration_token을 notification-be에 등록 요청
도메인 이벤트 발생 시 대상 User_TM.UserId 결정
template_code 또는 definition_code 결정
notification-be에 발송 요청
```

각 서비스 backend에는 Firebase Admin SDK service account JSON이 필요 없다.

### 7.3 notification-be에 전달할 값

```env
GOOGLE_APPLICATION_CREDENTIALS=...
GOOGLE_CLOUD_PROJECT=...
```

notification-be가 하는 일:

```text
User_TM 조회
NotificationDevice_TM 조회
NotificationTemplate_TM 조회
Firebase Admin SDK로 FCM 발송
NotificationMessage_TM 발송 이력 저장
```

## 8. 회사 프로젝트별 관리표 예시

| 구분 | Firebase project | Web app nickname | Frontend env | Backend 역할 | 사용자 기준 |
| --- | --- | --- | --- | --- | --- |
| TVCF Web dev | company-fcm-dev | tvcf-web-dev | dev Web app config + dev VAPID | notification-be dev 호출 | User_TM.UserId |
| AdMarket Web dev | company-fcm-dev | admarket-web-dev | dev Web app config + dev VAPID | notification-be dev 호출 | User_TM.UserId |
| Coding_Quiz test | coding-quiz-fcm-test | coding-quiz-local-test | test Web app config + test VAPID | local notification-be 호출 | Coding_Quiz 로그인 username |
| TVCF Web prod | company-fcm-prod | tvcf-web-prod | prod Web app config + prod VAPID | notification-be prod 호출 | User_TM.UserId |

관리 원칙:

```text
dev frontend는 dev Firebase project 값을 사용
prod frontend는 prod Firebase project 값을 사용
dev notification-be는 dev service account 사용
prod notification-be는 prod service account 사용
```

dev/prod가 섞이면 token과 발송 credential이 어긋난다.

## 9. 현재 로컬 테스트 값의 의미

현재 개인 테스트 프로젝트 기준:

```text
Firebase project:
coding-quiz-fcm-test

Frontend:
Coding_Quiz/frontend/.env.local

notification-be:
GOOGLE_APPLICATION_CREDENTIALS
GOOGLE_CLOUD_PROJECT
```

이 테스트의 의미:

```text
Coding_Quiz frontend가 FCM token을 발급
Coding_Quiz backend가 token 등록과 발송 요청을 notification-be로 프록시
notification-be가 로컬 tvcf_dev DB에서 user/template/device를 조회
notification-be가 Firebase Admin SDK로 실제 FCM 발송
브라우저의 foreground 수신 로그에서 payload 확인
```

개인 Firebase 프로젝트는 로컬 검증용이다. 회사 프로젝트에 붙일 때는 회사 Firebase 프로젝트의 Web app config, VAPID key, service account로 바꿔야 한다.

## 10. 검증 체크리스트

Frontend:

```text
NEXT_PUBLIC_FIREBASE_PROJECT_ID가 의도한 Firebase project인지
NEXT_PUBLIC_FIREBASE_VAPID_KEY가 같은 Firebase project에서 생성된 값인지
.env.local 변경 후 frontend를 재시작했는지
브라우저 알림 권한이 granted인지
FCM registration token이 발급되는지
foreground 수신 로그가 켜져 있는지
```

notification-be:

```text
GOOGLE_APPLICATION_CREDENTIALS 경로가 실제 JSON 파일을 가리키는지
JSON 안의 project_id가 frontend projectId와 같은지
GOOGLE_CLOUD_PROJECT가 같은 projectId인지
환경변수 설정 후 notification-be를 재시작했는지
```

DB:

```text
User_TM에 대상 UserId가 있는지
NotificationDevice_TM에 대상 UserId의 token이 있는지
NotificationTemplate_TM에 template_code가 있는지
발송 후 NotificationMessage_TM 이력이 저장되는지
```

성공 기준:

```text
/v1/devices token 등록 성공
/v1/messages:sendUser 응답 success_count=1
NotificationMessage_TM status=SUCCESS
브라우저 foreground 수신 로그에 payload 표시
```

## 11. 자주 하는 실수

```text
frontend Firebase project와 notification-be service account project가 다름
VAPID key가 다른 Firebase project 값임
service account JSON을 frontend에 넣음
service account JSON을 Git에 커밋함
GOOGLE_APPLICATION_CREDENTIALS를 다른 터미널에만 설정함
.env.local 변경 후 frontend를 재시작하지 않음
notification-be env 변경 후 uvicorn을 재시작하지 않음
개인 테스트 Firebase 값을 회사 운영 환경에 그대로 사용함
```

## 12. 공식 문서

Firebase Web app 등록과 config:

```text
https://firebase.google.com/docs/web/setup
```

FCM Web client, VAPID key, getToken:

```text
https://firebase.google.com/docs/cloud-messaging/js/client
```

FCM foreground 수신:

```text
https://firebase.google.com/docs/cloud-messaging/js/receive
```

Firebase Admin SDK와 service account:

```text
https://firebase.google.com/docs/admin/setup
```

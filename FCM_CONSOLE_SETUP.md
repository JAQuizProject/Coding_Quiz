# FCM Console Setup Guide

이 문서는 `Coding_Quiz`로 notification-be FCM 발송을 테스트하기 위해 Firebase Console에서 준비해야 할 값만 정리한다.

## 핵심 원칙

아래 값들은 같은 Firebase 프로젝트 기준이어야 한다.

```text
Frontend Firebase projectId
Frontend VAPID key
notification-be service account JSON
notification-be GOOGLE_CLOUD_PROJECT
```

서로 다른 Firebase 프로젝트 값이 섞이면 token 발급은 되더라도 FCM 발송이 실패할 수 있다.

## 1. Firebase 프로젝트 준비

Firebase Console:

```text
https://console.firebase.google.com
```

테스트용 개인 프로젝트를 만들거나 기존 테스트 프로젝트를 사용한다.

예:

```text
coding-quiz-fcm-test
```

## 2. Web app 등록

경로:

```text
Firebase Console
  -> Project settings
  -> General
  -> Your apps
  -> Web app 추가 또는 선택
```

frontend에 넣을 값:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...
```

이 값들은 Firebase Web SDK 초기화에 사용한다.

## 3. VAPID public key 준비

경로:

```text
Firebase Console
  -> Project settings
  -> Cloud Messaging
  -> Web configuration
  -> Web Push certificates
  -> Generate key pair
```

frontend에 넣을 값:

```env
NEXT_PUBLIC_FIREBASE_VAPID_KEY=...
```

사용 위치:

```text
Firebase Web SDK getToken(messaging, { vapidKey })
```

## 4. Service account JSON 준비

경로:

```text
Firebase Console
  -> Project settings
  -> Service accounts
  -> Firebase Admin SDK
  -> Generate new private key
```

notification-be 실행 환경에 넣을 값:

```env
GOOGLE_APPLICATION_CREDENTIALS=<service account JSON 경로>
GOOGLE_CLOUD_PROJECT=<Firebase project id>
```

주의:

```text
service account JSON은 서버 비밀키다.
Git에 커밋하지 않는다.
frontend에 넣지 않는다.
repo 밖 경로에 둔다.
```

## 5. Coding_Quiz frontend env

파일:

```text
frontend/.env.local
```

예:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=coding-quiz-fcm-test
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...
NEXT_PUBLIC_FIREBASE_VAPID_KEY=...

NEXT_PUBLIC_NOTIFICATION_TEST_TEMPLATE_CODE=<notification-be template code>
```

## 6. notification-be env

예:

```env
GOOGLE_APPLICATION_CREDENTIALS=C:/Users/gram/.secrets/coding-quiz-fcm-test-firebase-adminsdk.json
GOOGLE_CLOUD_PROJECT=coding-quiz-fcm-test
```

env 변경 후에는 notification-be를 재시작한다.

## 확인 기준

```text
FCM token 발급 성공
Token 등록 성공
sendUser success_count=1
/fcm-test foreground 수신 로그 표시
```

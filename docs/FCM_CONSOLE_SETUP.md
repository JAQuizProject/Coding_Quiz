# FCM Console Setup Guide

이 문서는 `/fcm-test` 실행 전에 Firebase Console에서 준비해야 하는 값만 정리한다.

## 같은 프로젝트 값을 써야 함

아래 값은 모두 같은 Firebase 프로젝트에서 가져와야 한다.

```text
Coding_Quiz frontend Firebase config
Coding_Quiz frontend VAPID key
notification-be service account JSON
notification-be GOOGLE_CLOUD_PROJECT
```

서로 다른 프로젝트 값이 섞이면 token 발급은 되더라도 notification-be의 FCM 발송이 실패할 수 있다.

## 1. Web app config

경로:

```text
Firebase Console
  -> Project settings
  -> General
  -> Your apps
  -> Web app
```

`frontend/.env.local`에 넣는다.

```env
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...
```

## 2. VAPID key

경로:

```text
Firebase Console
  -> Project settings
  -> Cloud Messaging
  -> Web configuration
  -> Web Push certificates
```

`frontend/.env.local`에 넣는다.

```env
NEXT_PUBLIC_FIREBASE_VAPID_KEY=...
```

## 3. Service account JSON

경로:

```text
Firebase Console
  -> Project settings
  -> Service accounts
  -> Firebase Admin SDK
  -> Generate new private key
```

notification-be 실행 환경에 넣는다.

```env
GOOGLE_APPLICATION_CREDENTIALS=C:/Users/gram/.secrets/firebase-adminsdk.json
GOOGLE_CLOUD_PROJECT=<Firebase project id>
```

주의:

- service account JSON은 repo에 커밋하지 않는다.
- frontend env에 넣지 않는다.
- `C:/Users/gram/.secrets/...`처럼 repo 밖에 둔다.

## 확인 기준

1. `/fcm-test`에서 FCM token 발급 성공
2. notification-be `/v1/devices` 등록 성공
3. sendUser 또는 sendDefinition 응답이 `success_count=1`
4. `/fcm-test` foreground 수신 로그에 title/body 표시

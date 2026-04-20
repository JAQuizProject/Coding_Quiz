"use client";

import { initializeApp, getApp, getApps } from "firebase/app";
import {
  getMessaging,
  getToken,
  isSupported,
  onMessage,
} from "firebase/messaging";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  getNotificationTestConfig,
  registerNotificationDevice,
  sendDefinitionNotificationTest,
  sendNotificationTest,
} from "../../api/notificationTest";
import styles from "./page.module.css";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

const firebaseEnvLabels = [
  ["NEXT_PUBLIC_FIREBASE_API_KEY", firebaseConfig.apiKey],
  ["NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN", firebaseConfig.authDomain],
  ["NEXT_PUBLIC_FIREBASE_PROJECT_ID", firebaseConfig.projectId],
  ["NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID", firebaseConfig.messagingSenderId],
  ["NEXT_PUBLIC_FIREBASE_APP_ID", firebaseConfig.appId],
  ["NEXT_PUBLIC_FIREBASE_VAPID_KEY", process.env.NEXT_PUBLIC_FIREBASE_VAPID_KEY],
];

function createLogEntry(source, payload) {
  const data = payload?.data || {};
  const notification = payload?.notification || {};

  return {
    id: `${Date.now()}-${Math.random()}`,
    source,
    title: data.title || notification.title || "(no title)",
    body: data.body || notification.body || "(no body)",
    receivedAt: new Date().toLocaleString(),
    payload,
  };
}

function formatValue(value) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  if (typeof value === "string") {
    return value;
  }

  return JSON.stringify(value, null, 2);
}

function getErrorMessage(error) {
  const message = error?.message || String(error);
  return error?.code ? `${message} (${error.code})` : message;
}

function formatSendSummary(label, responseBody) {
  return `${label}: target ${formatValue(responseBody.target_count)}, success ${formatValue(
    responseBody.success_count,
  )}, failure ${formatValue(responseBody.failure_count)}`;
}

async function getReadyMessagingRegistration(firebaseConfig) {
  const registration = await navigator.serviceWorker.register("/firebase-messaging-sw.js", {
    scope: "/",
  });
  const readyRegistration = await navigator.serviceWorker.ready;
  const messagingRegistration = readyRegistration || registration;
  const activeWorker = messagingRegistration.active;

  if (!activeWorker) {
    throw new Error("FCM service worker가 아직 활성화되지 않았습니다. 페이지를 새로고침한 뒤 다시 시도하세요.");
  }

  await new Promise((resolve, reject) => {
    const channel = new MessageChannel();
    const timeoutId = window.setTimeout(() => {
      reject(new Error("FCM service worker 초기화 응답 시간이 초과되었습니다."));
    }, 5000);

    channel.port1.onmessage = (event) => {
      window.clearTimeout(timeoutId);
      if (event.data?.ok) {
        resolve();
        return;
      }
      reject(new Error(event.data?.error || "FCM service worker 초기화에 실패했습니다."));
    };

    activeWorker.postMessage(
      {
        type: "FIREBASE_MESSAGING_CONFIG",
        firebaseConfig,
      },
      [channel.port2],
    );
  });

  return messagingRegistration;
}

export default function FcmTestPage() {
  const [permission, setPermission] = useState("default");
  const [token, setToken] = useState("");
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState("");
  const [tokenStatus, setTokenStatus] = useState("");
  const [registrationStatus, setRegistrationStatus] = useState("");
  const [userSendStatus, setUserSendStatus] = useState("");
  const [definitionSendStatus, setDefinitionSendStatus] = useState("");
  const [serverConfig, setServerConfig] = useState(null);
  const [notificationUserId, setNotificationUserId] = useState("");
  const [userTemplateCode, setUserTemplateCode] = useState(
    process.env.NEXT_PUBLIC_NOTIFICATION_TEST_TEMPLATE_CODE || "",
  );
  const [definitionCode, setDefinitionCode] = useState(
    process.env.NEXT_PUBLIC_NOTIFICATION_TEST_DEFINITION_CODE || "",
  );
  const [definitionTemplateCode, setDefinitionTemplateCode] = useState(
    process.env.NEXT_PUBLIC_NOTIFICATION_TEST_TEMPLATE_CODE || "",
  );
  const [isIssuingToken, setIsIssuingToken] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [isSendingUser, setIsSendingUser] = useState(false);
  const [isSendingDefinition, setIsSendingDefinition] = useState(false);
  const unsubscribeRef = useRef(null);

  const missingEnv = useMemo(
    () => firebaseEnvLabels.filter(([, value]) => !value).map(([label]) => label),
    [],
  );

  const appendLog = useCallback((source, payload) => {
    setLogs((current) => [createLogEntry(source, payload), ...current].slice(0, 20));
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined" && "Notification" in window) {
      setPermission(Notification.permission);
    }

    getNotificationTestConfig().then((result) => {
      if (!result?.error) {
        setServerConfig(result);
        setUserTemplateCode((current) => current || result.default_template_code || "");
        setDefinitionTemplateCode((current) => current || result.default_template_code || "");
        setDefinitionCode((current) => current || result.default_definition_code || "");
      }
    });
  }, []);

  useEffect(() => {
    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
        unsubscribeRef.current = null;
      }
    };
  }, []);

  const issueToken = async () => {
    setError("");
    setTokenStatus("");
    setIsIssuingToken(true);

    try {
      if (missingEnv.length > 0) {
        throw new Error(`Firebase 환경변수가 없습니다: ${missingEnv.join(", ")}`);
      }
      if (!("Notification" in window)) {
        throw new Error("이 브라우저는 Notification API를 지원하지 않습니다.");
      }
      if (!("serviceWorker" in navigator)) {
        throw new Error("이 브라우저는 Service Worker를 지원하지 않습니다.");
      }
      if (!window.isSecureContext) {
        throw new Error("FCM Web Push는 localhost 또는 HTTPS에서만 사용할 수 있습니다.");
      }

      const supported = await isSupported();
      if (!supported) {
        throw new Error("현재 브라우저에서는 Firebase Messaging을 사용할 수 없습니다.");
      }

      const nextPermission = await Notification.requestPermission();
      setPermission(nextPermission);
      if (nextPermission !== "granted") {
        throw new Error("브라우저 알림 권한이 필요합니다.");
      }

      const app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
      const messaging = getMessaging(app);
      const registration = await getReadyMessagingRegistration(firebaseConfig);

      if (unsubscribeRef.current) {
        unsubscribeRef.current();
      }
      unsubscribeRef.current = onMessage(messaging, (payload) => {
        appendLog("foreground", payload);
      });

      const registrationToken = await getToken(messaging, {
        vapidKey: process.env.NEXT_PUBLIC_FIREBASE_VAPID_KEY,
        serviceWorkerRegistration: registration,
      });

      if (!registrationToken) {
        throw new Error("FCM token을 발급받지 못했습니다.");
      }

      setToken(registrationToken);
      setTokenStatus("FCM token 발급 완료. 이 페이지를 열어두면 foreground 메시지를 받을 수 있습니다.");
    } catch (nextError) {
      setError(getErrorMessage(nextError));
    } finally {
      setIsIssuingToken(false);
    }
  };

  const copyToken = async () => {
    if (!token) return;
    await navigator.clipboard.writeText(token);
    setTokenStatus("FCM token을 복사했습니다.");
  };

  const registerDevice = async () => {
    if (!token) {
      setError("먼저 FCM token을 발급하세요.");
      return;
    }

    setError("");
    setRegistrationStatus("");
    setIsRegistering(true);
    const result = await registerNotificationDevice(token);
    setIsRegistering(false);

    if (result?.error) {
      setError(formatValue(result.error));
      return;
    }

    if (result.notification_user_id) {
      setNotificationUserId(result.notification_user_id);
    }
    setRegistrationStatus(`디바이스 등록 완료: ${formatValue(result.notification_response?.body?.code)}`);
  };

  const sendUserNotification = async () => {
    setError("");
    setUserSendStatus("");
    setIsSendingUser(true);
    const result = await sendNotificationTest({
      templateCode: userTemplateCode.trim(),
    });
    setIsSendingUser(false);

    if (result?.error) {
      setError(formatValue(result.error));
      return;
    }

    if (result.notification_user_id) {
      setNotificationUserId(result.notification_user_id);
    }
    const responseBody = result.notification_response?.body || {};
    setUserSendStatus(formatSendSummary("유저 직접 발송 완료", responseBody));
  };

  const sendDefinitionNotification = async () => {
    setError("");
    setDefinitionSendStatus("");
    setIsSendingDefinition(true);
    const result = await sendDefinitionNotificationTest({
      definitionCode: definitionCode.trim(),
      templateCode: definitionTemplateCode.trim(),
    });
    setIsSendingDefinition(false);

    if (result?.error) {
      setError(formatValue(result.error));
      return;
    }

    if (result.notification_user_id) {
      setNotificationUserId(result.notification_user_id);
    }
    const responseBody = result.notification_response?.body || {};
    setDefinitionSendStatus(formatSendSummary("구독 기반 발송 완료", responseBody));
  };

  return (
    <main className={styles.page}>
      <section className={styles.header}>
        <p className={styles.kicker}>FCM live test</p>
        <h1 className={styles.title}>Foreground 알림 테스트</h1>
        <p className={styles.lead}>
          개인 Firebase 프로젝트에서 발급한 Web Push token으로 notification-be 발송 흐름을 확인합니다.
        </p>
      </section>

      <section className={styles.grid}>
        <div className={styles.panel}>
          <h2 className={styles.panelTitle}>1. Token 발급</h2>
          <p className={styles.panelText}>
            브라우저가 Firebase FCM 메시지를 받을 수 있는 registration token을 발급합니다.
          </p>
          <p className={styles.metaText}>권한 상태: {permission}</p>
          {missingEnv.length > 0 && (
            <p className={styles.warning}>필요한 Firebase 환경변수: {missingEnv.join(", ")}</p>
          )}
          <button className={styles.primaryButton} onClick={issueToken} disabled={isIssuingToken}>
            {isIssuingToken ? "발급 중" : "FCM token 발급"}
          </button>
          <textarea className={styles.tokenBox} value={token} readOnly placeholder="FCM token" />
          <button className={styles.secondaryButton} onClick={copyToken} disabled={!token}>
            Token 복사
          </button>
          {tokenStatus && <p className={styles.success}>{tokenStatus}</p>}
        </div>

        <div className={styles.panel}>
          <h2 className={styles.panelTitle}>2. Token 등록</h2>
          <p className={styles.panelText}>
            로그인한 CodingQuiz username을 notification-be UserId로 사용해서 현재 브라우저 token을 등록합니다.
          </p>
          <dl className={styles.configList}>
            <dt>Base URL</dt>
            <dd>{serverConfig?.notification_base_url || "-"}</dd>
            <dt>Device API</dt>
            <dd>{serverConfig?.device_path || "-"}</dd>
            <dt>Send User API</dt>
            <dd>{serverConfig?.send_user_path || "-"}</dd>
            <dt>Send Definition API</dt>
            <dd>{serverConfig?.send_definition_path || "-"}</dd>
          </dl>
          <button
            className={styles.secondaryButton}
            onClick={registerDevice}
            disabled={!token || isRegistering}
          >
            {isRegistering ? "등록 중" : "Token 등록"}
          </button>
          {registrationStatus && <p className={styles.success}>{registrationStatus}</p>}
        </div>

        <div className={styles.panel}>
          <h2 className={styles.panelTitle}>3. 유저 직접 발송</h2>
          <p className={styles.panelText}>
            subscription 없이 로그인 username과 template code로 /v1/messages:sendUser를 호출합니다.
          </p>
          <p className={styles.panelText}>
            User ID: {notificationUserId || "CodingQuiz 로그인 유저 기준 자동 적용"}
          </p>
          <label className={styles.label}>
            Template code
            <input
              className={styles.input}
              value={userTemplateCode}
              onChange={(event) => setUserTemplateCode(event.target.value)}
              placeholder="NotificationTemplate code"
            />
          </label>
          <button className={styles.primaryButton} onClick={sendUserNotification} disabled={isSendingUser}>
            {isSendingUser ? "발송 중" : "sendUser 발송 요청"}
          </button>
          {userSendStatus && <p className={styles.success}>{userSendStatus}</p>}
        </div>

        <div className={styles.panel}>
          <h2 className={styles.panelTitle}>4. 구독 기반 발송</h2>
          <p className={styles.panelText}>
            NotificationSubscription_TM에 연결된 유저들에게 /v1/messages:sendDefinition으로 발송합니다.
          </p>
          <p className={styles.metaText}>
            현재 로그인 username이 해당 definition을 구독하고 있고, token 등록이 되어 있어야 수신됩니다.
          </p>
          <label className={styles.label}>
            Definition code
            <input
              className={styles.input}
              value={definitionCode}
              onChange={(event) => setDefinitionCode(event.target.value)}
              placeholder="NotificationDefinition code"
            />
          </label>
          <label className={styles.label}>
            Template code
            <input
              className={styles.input}
              value={definitionTemplateCode}
              onChange={(event) => setDefinitionTemplateCode(event.target.value)}
              placeholder="NotificationTemplate code"
            />
          </label>
          <button
            className={styles.primaryButton}
            onClick={sendDefinitionNotification}
            disabled={isSendingDefinition}
          >
            {isSendingDefinition ? "발송 중" : "sendDefinition 발송 요청"}
          </button>
          {definitionSendStatus && <p className={styles.success}>{definitionSendStatus}</p>}
        </div>

        <div className={`${styles.panel} ${styles.widePanel}`}>
          <h2 className={styles.panelTitle}>5. Foreground 수신 로그</h2>
          {error && <pre className={styles.error}>{error}</pre>}
          <div className={styles.logList}>
            {logs.length === 0 ? (
              <p className={styles.empty}>수신 대기 중입니다.</p>
            ) : (
              logs.map((log) => (
                <article className={styles.logItem} key={log.id}>
                  <div className={styles.logMeta}>
                    <span>{log.source}</span>
                    <time>{log.receivedAt}</time>
                  </div>
                  <strong>{log.title}</strong>
                  <p>{log.body}</p>
                  <pre>{JSON.stringify(log.payload, null, 2)}</pre>
                </article>
              ))
            )}
          </div>
        </div>
      </section>
    </main>
  );
}

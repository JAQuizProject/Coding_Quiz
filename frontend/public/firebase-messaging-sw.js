importScripts("https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging-compat.js");

let messagingInitialized = false;

function broadcastPayload(payload) {
  self.clients.matchAll({ includeUncontrolled: true, type: "window" }).then((clients) => {
    clients.forEach((client) => {
      client.postMessage({
        type: "FCM_BACKGROUND_MESSAGE",
        payload,
      });
    });
  });
}

function initializeMessaging(firebaseConfig) {
  if (messagingInitialized) {
    return;
  }

  firebase.initializeApp(firebaseConfig);
  const messaging = firebase.messaging();

  messaging.onBackgroundMessage((payload) => {
    const data = payload.data || {};
    const notification = payload.notification || {};
    const title = data.title || notification.title || "Coding Quiz";
    const body = data.body || notification.body || "FCM message received.";

    broadcastPayload(payload);

    self.registration.showNotification(title, {
      body,
      data: payload,
    });
  });

  messagingInitialized = true;
}

self.addEventListener("message", (event) => {
  if (event.data?.type === "FIREBASE_MESSAGING_CONFIG") {
    initializeMessaging(event.data.firebaseConfig);
  }
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(self.clients.openWindow("/fcm-test"));
});

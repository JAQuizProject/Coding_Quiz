importScripts("https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging-compat.js");

let messagingInitialized = false;

function initializeMessaging(firebaseConfig) {
  if (messagingInitialized) {
    return;
  }

  firebase.initializeApp(firebaseConfig);
  firebase.messaging();
  messagingInitialized = true;
}

self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("message", (event) => {
  if (event.data?.type === "FIREBASE_MESSAGING_CONFIG") {
    try {
      initializeMessaging(event.data.firebaseConfig);
      event.ports?.[0]?.postMessage({ ok: true });
    } catch (error) {
      event.ports?.[0]?.postMessage({
        ok: false,
        error: error?.message || String(error),
      });
    }
  }
});

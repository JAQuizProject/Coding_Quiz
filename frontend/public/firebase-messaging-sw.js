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

self.addEventListener("message", (event) => {
  if (event.data?.type === "FIREBASE_MESSAGING_CONFIG") {
    initializeMessaging(event.data.firebaseConfig);
  }
});

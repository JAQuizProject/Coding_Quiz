const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function requestJson(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    return {
      error: data?.detail || data || `HTTP ${response.status}`,
      status: response.status,
    };
  }

  return data;
}

export function getNotificationTestConfig() {
  return requestJson("/fcm-test/config");
}

export function registerNotificationDevice(registrationToken) {
  return requestJson("/fcm-test/register-device", {
    method: "POST",
    body: JSON.stringify({
      registration_token: registrationToken,
    }),
  });
}

export function sendNotificationTest({ userId, templateCode }) {
  return requestJson("/fcm-test/send", {
    method: "POST",
    body: JSON.stringify({
      user_id: userId || null,
      template_code: templateCode || null,
    }),
  });
}

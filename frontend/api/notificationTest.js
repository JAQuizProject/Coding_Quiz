const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function requestJson(path, options = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
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

export function sendNotificationTest({ templateCode }) {
  return requestJson("/fcm-test/send", {
    method: "POST",
    body: JSON.stringify({
      template_code: templateCode || null,
    }),
  });
}

export function sendDefinitionNotificationTest({ definitionCode, templateCode }) {
  return requestJson("/fcm-test/send-definition", {
    method: "POST",
    body: JSON.stringify({
      definition_code: definitionCode || null,
      template_code: templateCode || null,
    }),
  });
}

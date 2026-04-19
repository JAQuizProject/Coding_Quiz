import io
import json
from urllib.error import HTTPError

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import config
from app.modules.notification_test import service as notification_service
from app.modules.notification_test.router import get_optional_current_user
from main import app


CONFIG_FIELDS = (
    "FCM_TEST_PROXY_ENABLED",
    "TVCF_NOTIFICATION_BASE_URL",
    "TVCF_NOTIFICATION_DEVICE_PATH",
    "TVCF_NOTIFICATION_SEND_USER_PATH",
    "TVCF_NOTIFICATION_AUTH_TOKEN",
    "TVCF_NOTIFICATION_USER_AGENT",
    "TVCF_NOTIFICATION_TIMEOUT_SECONDS",
    "FCM_TEST_TEMPLATE_CODE",
)


class FakeResponse:
    def __init__(self, status: int, body: dict):
        self.status = status
        self._body = json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return self._body


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def restore_config():
    original_values = {field: getattr(config, field) for field in CONFIG_FIELDS}
    yield
    for field, value in original_values.items():
        setattr(config, field, value)
    app.dependency_overrides.pop(get_optional_current_user, None)


def _headers(request):
    return {key.lower(): value for key, value in request.header_items()}


def override_current_user(username: str) -> None:
    current_user = type("FakeUser", (), {"username": username})()
    app.dependency_overrides[get_optional_current_user] = lambda: current_user


def test_get_fcm_test_config(client):
    config.FCM_TEST_PROXY_ENABLED = True
    config.TVCF_NOTIFICATION_BASE_URL = "http://notification.test"
    config.TVCF_NOTIFICATION_DEVICE_PATH = "/v1/devices"
    config.TVCF_NOTIFICATION_SEND_USER_PATH = "/v1/messages:sendUser"
    config.FCM_TEST_TEMPLATE_CODE = "TPL-1"

    response = client.get("/fcm-test/config")

    assert response.status_code == 200
    assert response.json() == {
        "enabled": True,
        "notification_base_url": "http://notification.test",
        "device_path": "/v1/devices",
        "send_user_path": "/v1/messages:sendUser",
        "default_template_code": "TPL-1",
    }


def test_register_device_posts_logged_in_user_to_notification_be(client, monkeypatch):
    captured = {}
    config.FCM_TEST_PROXY_ENABLED = True
    config.TVCF_NOTIFICATION_BASE_URL = "http://notification.test"
    config.TVCF_NOTIFICATION_DEVICE_PATH = "/v1/devices"
    config.TVCF_NOTIFICATION_TIMEOUT_SECONDS = 3
    override_current_user("quizuser")

    def fake_urlopen(outbound_request, timeout):
        captured["url"] = outbound_request.full_url
        captured["body"] = json.loads(outbound_request.data.decode("utf-8"))
        captured["headers"] = _headers(outbound_request)
        captured["timeout"] = timeout
        return FakeResponse(201, {"code": "DEVICE-1", "token": "fcm-token"})

    monkeypatch.setattr(notification_service.request, "urlopen", fake_urlopen)

    response = client.post(
        "/fcm-test/register-device",
        headers={"User-Agent": "CodingQuiz-Test/1.0"},
        json={"registration_token": "fcm-token"},
    )

    assert response.status_code == 200
    assert captured["url"] == "http://notification.test/v1/devices"
    assert captured["body"] == {"registration_token": "fcm-token"}
    token = captured["headers"]["cookie"].removeprefix("access_token=")
    assert jwt.decode(token, options={"verify_signature": False})["userId"] == "quizuser"
    assert captured["headers"]["user-agent"] == "CodingQuiz-Test/1.0"
    assert captured["timeout"] == 3
    assert response.json()["notification_user_id"] == "quizuser"
    assert response.json()["notification_response"] == {
        "status_code": 201,
        "body": {"code": "DEVICE-1", "token": "fcm-token"},
    }


def test_register_device_uses_logged_in_user_and_browser_user_agent(client, monkeypatch):
    captured = {}
    config.FCM_TEST_PROXY_ENABLED = True
    config.TVCF_NOTIFICATION_BASE_URL = "http://notification.test"
    config.TVCF_NOTIFICATION_DEVICE_PATH = "/v1/devices"
    config.TVCF_NOTIFICATION_TIMEOUT_SECONDS = 3
    override_current_user("edgeuser")

    def fake_urlopen(outbound_request, timeout):
        captured["url"] = outbound_request.full_url
        captured["body"] = json.loads(outbound_request.data.decode("utf-8"))
        captured["headers"] = _headers(outbound_request)
        captured["timeout"] = timeout
        return FakeResponse(200, {"code": "DEVICE-1", "token": "fcm-token"})

    monkeypatch.setattr(notification_service.request, "urlopen", fake_urlopen)

    response = client.post(
        "/fcm-test/register-device",
        headers={"User-Agent": "Mozilla/5.0 Edg/122.0"},
        json={"registration_token": "fcm-token"},
    )

    assert response.status_code == 200
    assert captured["url"] == "http://notification.test/v1/devices"
    assert captured["body"] == {"registration_token": "fcm-token"}
    assert captured["headers"]["user-agent"] == "Mozilla/5.0 Edg/122.0"
    token = captured["headers"]["cookie"].removeprefix("access_token=")
    assert jwt.decode(token, options={"verify_signature": False})["userId"] == "edgeuser"
    assert response.json()["notification_user_id"] == "edgeuser"


def test_register_device_requires_login(client):
    config.FCM_TEST_PROXY_ENABLED = True

    response = client.post(
        "/fcm-test/register-device",
        json={"registration_token": "fcm-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "FCM 테스트는 Coding_Quiz 로그인이 필요합니다."


def test_send_posts_logged_in_user_and_template_code_to_notification_be(client, monkeypatch):
    captured = {}
    config.FCM_TEST_PROXY_ENABLED = True
    config.TVCF_NOTIFICATION_BASE_URL = "http://notification.test"
    config.TVCF_NOTIFICATION_SEND_USER_PATH = "/v1/messages:sendUser"
    override_current_user("quizuser")

    def fake_urlopen(outbound_request, timeout):
        captured["url"] = outbound_request.full_url
        captured["body"] = json.loads(outbound_request.data.decode("utf-8"))
        captured["headers"] = _headers(outbound_request)
        return FakeResponse(
            200,
            {
                "message_type": "user",
                "target_count": 1,
                "success_count": 1,
                "failure_count": 0,
            },
        )

    monkeypatch.setattr(notification_service.request, "urlopen", fake_urlopen)

    response = client.post(
        "/fcm-test/send",
        json={"template_code": "TPL-1"},
    )

    assert response.status_code == 200
    assert captured["url"] == "http://notification.test/v1/messages:sendUser"
    assert captured["body"] == {"user_id": "quizuser", "template_code": "TPL-1"}
    assert captured["headers"]["content-type"] == "application/json"
    assert response.json()["notification_user_id"] == "quizuser"
    assert response.json()["notification_response"]["body"] == {
        "message_type": "user",
        "target_count": 1,
        "success_count": 1,
        "failure_count": 0,
    }


def test_send_requires_login(client):
    config.FCM_TEST_PROXY_ENABLED = True

    response = client.post("/fcm-test/send", json={"template_code": "TPL-1"})

    assert response.status_code == 401
    assert response.json()["detail"] == "FCM 테스트는 Coding_Quiz 로그인이 필요합니다."


def test_send_requires_template_code(client):
    config.FCM_TEST_PROXY_ENABLED = True
    config.FCM_TEST_TEMPLATE_CODE = None
    override_current_user("quizuser")

    response = client.post("/fcm-test/send", json={})

    assert response.status_code == 400
    assert "template_code" in response.json()["detail"]


def test_notification_be_error_is_wrapped_as_502(client, monkeypatch):
    config.FCM_TEST_PROXY_ENABLED = True
    config.TVCF_NOTIFICATION_BASE_URL = "http://notification.test"
    config.TVCF_NOTIFICATION_SEND_USER_PATH = "/v1/messages:sendUser"
    override_current_user("quizuser")

    def fake_urlopen(outbound_request, timeout):
        raise HTTPError(
            url=outbound_request.full_url,
            code=500,
            msg="Internal Server Error",
            hdrs={},
            fp=io.BytesIO(b'{"detail":"boom"}'),
        )

    monkeypatch.setattr(notification_service.request, "urlopen", fake_urlopen)

    response = client.post(
        "/fcm-test/send",
        json={"template_code": "TPL-1"},
    )

    assert response.status_code == 502
    detail = response.json()["detail"]
    assert detail["target_url"] == "http://notification.test/v1/messages:sendUser"
    assert detail["notification_status_code"] == 500
    assert detail["notification_body"] == {"detail": "boom"}
    assert detail["request_body"] == {"user_id": "quizuser", "template_code": "TPL-1"}


def test_fcm_test_proxy_disabled_returns_404(client):
    config.FCM_TEST_PROXY_ENABLED = False

    response = client.post(
        "/fcm-test/send",
        json={"template_code": "TPL-1"},
    )

    assert response.status_code == 404

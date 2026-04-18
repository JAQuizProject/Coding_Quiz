import json
from socket import timeout as SocketTimeout
from typing import Any
from urllib import error, request

from app.core.config import config
from app.modules.notification_test.schemas import NotificationProxyResult


class NotificationProxyError(Exception):
    def __init__(self, message: str, status_code: int | None = None, body: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class NotificationProxyService:
    def __init__(
        self,
        base_url: str,
        device_path: str,
        send_user_path: str,
        auth_token: str | None,
        access_token: str | None,
        user_agent: str,
        timeout_seconds: int,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.device_path = device_path if device_path.startswith("/") else f"/{device_path}"
        self.send_user_path = send_user_path if send_user_path.startswith("/") else f"/{send_user_path}"
        self.auth_token = auth_token
        self.access_token = access_token
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds

    @property
    def device_url(self) -> str:
        return f"{self.base_url}{self.device_path}"

    @property
    def send_user_url(self) -> str:
        return f"{self.base_url}{self.send_user_path}"

    def register_device(self, registration_token: str) -> NotificationProxyResult:
        if not self.access_token:
            raise NotificationProxyError(
                "TVCF_NOTIFICATION_ACCESS_TOKEN is required to register a device.",
            )

        return self._post_json(
            url=self.device_url,
            body={"registration_token": registration_token},
            extra_headers={
                "Cookie": f"access_token={self.access_token}",
                "User-Agent": self.user_agent,
            },
        )

    def send_user_message(self, user_id: str, template_code: str) -> NotificationProxyResult:
        return self._post_json(
            url=self.send_user_url,
            body={
                "user_id": user_id,
                "template_code": template_code,
            },
            extra_headers=None,
        )

    def _post_json(
        self,
        url: str,
        body: dict[str, str],
        extra_headers: dict[str, str] | None,
    ) -> NotificationProxyResult:
        payload = json.dumps(body).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        if extra_headers:
            headers.update(extra_headers)

        outbound_request = request.Request(
            url,
            data=payload,
            headers=headers,
            method="POST",
        )

        try:
            with request.urlopen(outbound_request, timeout=self.timeout_seconds) as response:
                raw_body = response.read().decode("utf-8")
                return NotificationProxyResult(
                    status_code=response.status,
                    body=_parse_response_body(raw_body),
                )
        except error.HTTPError as exc:
            raw_body = exc.read().decode("utf-8", errors="replace")
            raise NotificationProxyError(
                "notification-be returned an error response.",
                status_code=exc.code,
                body=_parse_response_body(raw_body),
            ) from exc
        except (error.URLError, SocketTimeout, TimeoutError) as exc:
            raise NotificationProxyError(
                f"notification-be request failed: {exc}",
            ) from exc


def _parse_response_body(raw_body: str) -> dict[str, Any] | str | None:
    if not raw_body:
        return None

    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError:
        return raw_body

    if isinstance(parsed, dict):
        return parsed

    return {"value": parsed}


def get_notification_proxy_service() -> NotificationProxyService:
    return NotificationProxyService(
        base_url=config.TVCF_NOTIFICATION_BASE_URL,
        device_path=config.TVCF_NOTIFICATION_DEVICE_PATH,
        send_user_path=config.TVCF_NOTIFICATION_SEND_USER_PATH,
        auth_token=config.TVCF_NOTIFICATION_AUTH_TOKEN,
        access_token=config.TVCF_NOTIFICATION_ACCESS_TOKEN,
        user_agent=config.TVCF_NOTIFICATION_USER_AGENT,
        timeout_seconds=config.TVCF_NOTIFICATION_TIMEOUT_SECONDS,
    )

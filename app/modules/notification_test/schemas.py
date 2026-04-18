from typing import Any

from pydantic import Field

from app.core.schemas import APIModel


class NotificationTestConfigResponse(APIModel):
    enabled: bool
    notification_base_url: str
    device_path: str
    send_user_path: str
    default_user_id: str | None
    default_template_code: str | None
    has_notification_access_token: bool


class RegisterDeviceTestRequest(APIModel):
    registration_token: str = Field(min_length=1)


class SendNotificationTestRequest(APIModel):
    user_id: str | None = Field(default=None)
    template_code: str | None = Field(default=None)


class NotificationProxyResult(APIModel):
    status_code: int
    body: dict[str, Any] | str | None


class SendNotificationTestResponse(APIModel):
    message: str
    target_url: str
    request_body: dict[str, str]
    notification_response: NotificationProxyResult


class RegisterDeviceTestResponse(APIModel):
    message: str
    target_url: str
    request_body: dict[str, str]
    notification_response: NotificationProxyResult

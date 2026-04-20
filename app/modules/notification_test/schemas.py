from typing import Any

from pydantic import Field

from app.core.schemas import APIModel


class NotificationTestConfigResponse(APIModel):
    enabled: bool
    notification_base_url: str
    device_path: str
    subscription_path: str
    send_user_path: str
    send_definition_path: str
    default_template_code: str | None
    default_definition_code: str | None


class RegisterDeviceTestRequest(APIModel):
    registration_token: str = Field(min_length=1)


class SubscribeDefinitionTestRequest(APIModel):
    definition_code: str | None = Field(default=None)


class SendNotificationTestRequest(APIModel):
    template_code: str | None = Field(default=None)


class SendDefinitionNotificationTestRequest(APIModel):
    definition_code: str | None = Field(default=None)
    template_code: str | None = Field(default=None)


class NotificationProxyResult(APIModel):
    status_code: int
    body: dict[str, Any] | str | None


class SendNotificationTestResponse(APIModel):
    message: str
    target_url: str
    request_body: dict[str, str]
    notification_response: NotificationProxyResult
    notification_user_id: str | None = None


class RegisterDeviceTestResponse(APIModel):
    message: str
    target_url: str
    request_body: dict[str, str]
    notification_response: NotificationProxyResult
    notification_user_id: str | None = None


class SubscribeDefinitionTestResponse(APIModel):
    message: str
    target_url: str
    request_body: dict[str, str]
    notification_response: NotificationProxyResult
    notification_user_id: str

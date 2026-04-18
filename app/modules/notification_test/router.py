from fastapi import APIRouter, Depends, HTTPException

from app.core.config import config
from app.modules.notification_test.schemas import (
    NotificationTestConfigResponse,
    RegisterDeviceTestRequest,
    RegisterDeviceTestResponse,
    SendNotificationTestRequest,
    SendNotificationTestResponse,
)
from app.modules.notification_test.service import (
    NotificationProxyError,
    NotificationProxyService,
    get_notification_proxy_service,
)

router = APIRouter()


@router.get("/config", response_model=NotificationTestConfigResponse)
def get_notification_test_config() -> NotificationTestConfigResponse:
    return NotificationTestConfigResponse(
        enabled=config.FCM_TEST_PROXY_ENABLED,
        notification_base_url=config.TVCF_NOTIFICATION_BASE_URL,
        device_path=config.TVCF_NOTIFICATION_DEVICE_PATH,
        send_user_path=config.TVCF_NOTIFICATION_SEND_USER_PATH,
        default_user_id=config.FCM_TEST_USER_ID,
        default_template_code=config.FCM_TEST_TEMPLATE_CODE,
        has_notification_access_token=bool(config.TVCF_NOTIFICATION_ACCESS_TOKEN),
    )


@router.post("/register-device", response_model=RegisterDeviceTestResponse)
def register_test_device(
    payload: RegisterDeviceTestRequest,
    notification_proxy_service: NotificationProxyService = Depends(get_notification_proxy_service),
) -> RegisterDeviceTestResponse:
    if not config.FCM_TEST_PROXY_ENABLED:
        raise HTTPException(status_code=404, detail="FCM test proxy is disabled.")

    request_body = {"registration_token": payload.registration_token}

    try:
        notification_response = notification_proxy_service.register_device(
            registration_token=payload.registration_token,
        )
    except NotificationProxyError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": str(exc),
                "target_url": notification_proxy_service.device_url,
                "notification_status_code": exc.status_code,
                "notification_body": exc.body,
                "request_body": request_body,
            },
        ) from exc

    return RegisterDeviceTestResponse(
        message="notification-be 디바이스 등록 요청을 완료했습니다.",
        target_url=notification_proxy_service.device_url,
        request_body=request_body,
        notification_response=notification_response,
    )


@router.post("/send", response_model=SendNotificationTestResponse)
def send_test_notification(
    payload: SendNotificationTestRequest,
    notification_proxy_service: NotificationProxyService = Depends(get_notification_proxy_service),
) -> SendNotificationTestResponse:
    if not config.FCM_TEST_PROXY_ENABLED:
        raise HTTPException(status_code=404, detail="FCM test proxy is disabled.")

    user_id = payload.user_id or config.FCM_TEST_USER_ID
    template_code = payload.template_code or config.FCM_TEST_TEMPLATE_CODE
    if not user_id or not template_code:
        raise HTTPException(
            status_code=400,
            detail="user_id/template_code가 필요합니다. 요청 body나 .env의 FCM_TEST_USER_ID, FCM_TEST_TEMPLATE_CODE로 설정하세요.",
        )

    request_body = {
        "user_id": user_id,
        "template_code": template_code,
    }

    try:
        notification_response = notification_proxy_service.send_user_message(
            user_id=user_id,
            template_code=template_code,
        )
    except NotificationProxyError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": str(exc),
                "target_url": notification_proxy_service.send_user_url,
                "notification_status_code": exc.status_code,
                "notification_body": exc.body,
                "request_body": request_body,
            },
        ) from exc

    return SendNotificationTestResponse(
        message="notification-be 발송 요청을 완료했습니다.",
        target_url=notification_proxy_service.send_user_url,
        request_body=request_body,
        notification_response=notification_response,
    )

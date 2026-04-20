from fastapi import APIRouter, Depends, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import config
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.modules.notification_test.schemas import (
    NotificationTestConfigResponse,
    RegisterDeviceTestRequest,
    RegisterDeviceTestResponse,
    SendDefinitionNotificationTestRequest,
    SendNotificationTestRequest,
    SendNotificationTestResponse,
    SubscribeDefinitionTestRequest,
    SubscribeDefinitionTestResponse,
)
from app.modules.notification_test.service import (
    NotificationProxyError,
    NotificationProxyService,
    get_notification_proxy_service,
)

router = APIRouter()
security = HTTPBearer(auto_error=False)


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
    db: Session = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 토큰입니다.")

    user = db.query(User).filter(User.id == payload.id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    return user


def map_notification_user_id(user: User) -> str:
    notification_user_id = user.username.strip()
    if not notification_user_id:
        raise HTTPException(status_code=400, detail="notification-be UserId로 사용할 username이 없습니다.")
    if len(notification_user_id) > 20:
        raise HTTPException(
            status_code=400,
            detail="notification-be User_TM.UserId는 20자 이하입니다. 20자 이하 username으로 테스트하세요.",
        )
    return notification_user_id


def require_current_user(current_user: User | None) -> User:
    if current_user is None:
        raise HTTPException(status_code=401, detail="FCM 테스트는 Coding_Quiz 로그인이 필요합니다.")
    return current_user


@router.get("/config", response_model=NotificationTestConfigResponse)
def get_notification_test_config() -> NotificationTestConfigResponse:
    return NotificationTestConfigResponse(
        enabled=config.FCM_TEST_PROXY_ENABLED,
        notification_base_url=config.TVCF_NOTIFICATION_BASE_URL,
        device_path=config.TVCF_NOTIFICATION_DEVICE_PATH,
        subscription_path=config.TVCF_NOTIFICATION_SUBSCRIPTION_PATH,
        send_user_path=config.TVCF_NOTIFICATION_SEND_USER_PATH,
        send_definition_path=config.TVCF_NOTIFICATION_SEND_DEFINITION_PATH,
        default_template_code=config.FCM_TEST_TEMPLATE_CODE,
        default_definition_code=config.FCM_TEST_DEFINITION_CODE,
    )


@router.post("/register-device", response_model=RegisterDeviceTestResponse)
def register_test_device(
    request: Request,
    payload: RegisterDeviceTestRequest,
    current_user: User | None = Depends(get_optional_current_user),
    notification_proxy_service: NotificationProxyService = Depends(get_notification_proxy_service),
) -> RegisterDeviceTestResponse:
    if not config.FCM_TEST_PROXY_ENABLED:
        raise HTTPException(status_code=404, detail="FCM test proxy is disabled.")

    current_user = require_current_user(current_user)
    notification_user_id = map_notification_user_id(current_user)
    request_body = {"registration_token": payload.registration_token}
    request_body["notification_user_id"] = notification_user_id

    try:
        notification_response = notification_proxy_service.register_device(
            registration_token=payload.registration_token,
            notification_user_id=notification_user_id,
            user_agent=request.headers.get("User-Agent"),
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
        notification_user_id=notification_user_id,
    )


@router.post("/subscribe-definition", response_model=SubscribeDefinitionTestResponse)
def subscribe_test_definition(
    payload: SubscribeDefinitionTestRequest,
    current_user: User | None = Depends(get_optional_current_user),
    notification_proxy_service: NotificationProxyService = Depends(get_notification_proxy_service),
) -> SubscribeDefinitionTestResponse:
    if not config.FCM_TEST_PROXY_ENABLED:
        raise HTTPException(status_code=404, detail="FCM test proxy is disabled.")

    current_user = require_current_user(current_user)
    user_id = map_notification_user_id(current_user)
    definition_code = payload.definition_code or config.FCM_TEST_DEFINITION_CODE
    if not definition_code:
        raise HTTPException(
            status_code=400,
            detail="definition_code가 필요합니다. 요청 body나 .env의 FCM_TEST_DEFINITION_CODE로 설정하세요.",
        )

    request_body = {
        "user_id": user_id,
        "definition_code": definition_code,
    }

    try:
        notification_response = notification_proxy_service.subscribe_definition(
            user_id=user_id,
            definition_code=definition_code,
        )
    except NotificationProxyError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": str(exc),
                "target_url": notification_proxy_service.subscription_url,
                "notification_status_code": exc.status_code,
                "notification_body": exc.body,
                "request_body": request_body,
            },
        ) from exc

    return SubscribeDefinitionTestResponse(
        message="notification-be 구독 등록 요청을 완료했습니다.",
        target_url=notification_proxy_service.subscription_url,
        request_body=request_body,
        notification_response=notification_response,
        notification_user_id=user_id,
    )


@router.post("/send", response_model=SendNotificationTestResponse)
def send_test_notification(
    payload: SendNotificationTestRequest,
    current_user: User | None = Depends(get_optional_current_user),
    notification_proxy_service: NotificationProxyService = Depends(get_notification_proxy_service),
) -> SendNotificationTestResponse:
    if not config.FCM_TEST_PROXY_ENABLED:
        raise HTTPException(status_code=404, detail="FCM test proxy is disabled.")

    current_user = require_current_user(current_user)
    user_id = map_notification_user_id(current_user)
    template_code = payload.template_code or config.FCM_TEST_TEMPLATE_CODE
    if not template_code:
        raise HTTPException(
            status_code=400,
            detail="template_code가 필요합니다. 요청 body나 .env의 FCM_TEST_TEMPLATE_CODE로 설정하세요.",
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
        notification_user_id=user_id,
    )


@router.post("/send-definition", response_model=SendNotificationTestResponse)
def send_test_definition_notification(
    payload: SendDefinitionNotificationTestRequest,
    current_user: User | None = Depends(get_optional_current_user),
    notification_proxy_service: NotificationProxyService = Depends(get_notification_proxy_service),
) -> SendNotificationTestResponse:
    if not config.FCM_TEST_PROXY_ENABLED:
        raise HTTPException(status_code=404, detail="FCM test proxy is disabled.")

    current_user = require_current_user(current_user)
    notification_user_id = map_notification_user_id(current_user)
    definition_code = payload.definition_code or config.FCM_TEST_DEFINITION_CODE
    template_code = payload.template_code or config.FCM_TEST_TEMPLATE_CODE
    if not definition_code:
        raise HTTPException(
            status_code=400,
            detail="definition_code가 필요합니다. 요청 body나 .env의 FCM_TEST_DEFINITION_CODE로 설정하세요.",
        )
    if not template_code:
        raise HTTPException(
            status_code=400,
            detail="template_code가 필요합니다. 요청 body나 .env의 FCM_TEST_TEMPLATE_CODE로 설정하세요.",
        )

    request_body = {
        "definition_code": definition_code,
        "template_code": template_code,
    }

    try:
        notification_response = notification_proxy_service.send_definition_message(
            definition_code=definition_code,
            template_code=template_code,
        )
    except NotificationProxyError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": str(exc),
                "target_url": notification_proxy_service.send_definition_url,
                "notification_status_code": exc.status_code,
                "notification_body": exc.body,
                "request_body": request_body,
            },
        ) from exc

    return SendNotificationTestResponse(
        message="notification-be 구독 기반 발송 요청을 완료했습니다.",
        target_url=notification_proxy_service.send_definition_url,
        request_body=request_body,
        notification_response=notification_response,
        notification_user_id=notification_user_id,
    )

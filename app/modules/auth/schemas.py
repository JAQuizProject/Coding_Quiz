from pydantic import Field

from app.core.schemas import APIModel, MessageResponse


class SignupRequest(APIModel):
    username: str = Field(min_length=2, max_length=50)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=1, max_length=72)


class LoginRequest(APIModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=1, max_length=72)


class SignupUser(APIModel):
    id: str
    username: str
    email: str


class LoginUser(APIModel):
    id: str
    username: str


class SignupResponse(MessageResponse):
    user: SignupUser


class LoginResponse(MessageResponse):
    access_token: str
    user: LoginUser


class VerifyTokenResponse(MessageResponse):
    user: str


class LogoutResponse(MessageResponse):
    pass


# 기존 코드/임포트와의 호환성 유지
UserCreate = SignupRequest
UserLogin = LoginRequest

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    """프로젝트 전반에서 재사용하는 기본 Pydantic 모델."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class MessageResponse(APIModel):
    message: str

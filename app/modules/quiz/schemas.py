from typing import Optional

from pydantic import ConfigDict, Field, model_validator, field_validator

from app.core.schemas import APIModel, MessageResponse


class QuizListQuery(APIModel):
    category: Optional[str] = Field(default=None, max_length=100)

    @field_validator("category")
    @classmethod
    def normalize_category(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class QuizItem(APIModel):
    id: str
    question: str
    explanation: str
    answer: str


class QuizListResponse(MessageResponse):
    data: list[QuizItem]


class CategoryListResponse(MessageResponse):
    data: list[str]


class ScoreSubmitRequest(APIModel):
    # 프론트의 추가 필드(score)를 허용하기 위해 request만 ignore 적용
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    category: Optional[str] = Field(default=None, max_length=100)
    correct: int = Field(default=0, ge=0)
    total: int = Field(default=10, ge=0)
    score: Optional[float] = Field(default=None, ge=0, le=100)

    @field_validator("category")
    @classmethod
    def normalize_category(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_counts(self):
        if self.total == 0 and self.correct > 0:
            raise ValueError("total이 0이면 correct는 0이어야 합니다.")

        if self.total > 0 and self.correct > self.total:
            raise ValueError("correct는 total보다 클 수 없습니다.")

        return self


class ScoreSubmitResponse(MessageResponse):
    score: float = Field(ge=0, le=100)


# 기존 코드/임포트와의 호환성 유지
ScoreSubmit = ScoreSubmitRequest

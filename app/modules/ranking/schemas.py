from typing import Optional

from pydantic import Field, field_validator

from app.core.schemas import APIModel, MessageResponse


class RankingQuery(APIModel):
    category: Optional[str] = Field(default=None, max_length=100)
    limit: int = Field(default=10, ge=1, le=100)

    @field_validator("category")
    @classmethod
    def normalize_category(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class RankingItem(APIModel):
    rank: int = Field(ge=1)
    username: str
    score: int = Field(ge=0)
    category: str
    date: str


class RankingListResponse(MessageResponse):
    ranking: list[RankingItem]

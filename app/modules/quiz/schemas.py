from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ScoreSubmit(BaseModel):
    model_config = ConfigDict(extra="ignore")
    category: Optional[str] = Field(default=None)
    correct: int = Field(default=0, ge=0)
    total: int = Field(default=10, ge=0)

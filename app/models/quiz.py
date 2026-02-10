from sqlalchemy import Column, String

from ..core.database import Base
from ..core.ulid import generate_ulid


class Quiz(Base):
    """퀴즈(Quiz) 테이블 정의"""

    __tablename__ = "quizzes"
    __table_args__ = {"extend_existing": True}

    id = Column(String(26), primary_key=True, index=True, default=generate_ulid)
    question = Column(String, nullable=False)
    explanation = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    category = Column(String, nullable=False)

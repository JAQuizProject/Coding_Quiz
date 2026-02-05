from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from ..core.database import Base


class Score(Base):
    """사용자 점수(Score) 테이블 정의"""

    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 사용자 ID (외래키)
    category = Column(String, nullable=False)  # 카테고리
    score = Column(Integer, nullable=False)  # 점수
    created_at = Column(DateTime, default=func.now())  # 점수 저장 시간

    user = relationship("User", back_populates="scores")  # User 테이블과 연결

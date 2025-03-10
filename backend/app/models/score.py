from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..core.database import Base

class Score(Base):
    """사용자 점수(Score) 테이블 정의"""

    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 외래키 설정
    score = Column(Integer, nullable=False)  # 퀴즈 점수 저장
    created_at = Column(DateTime, default=func.now())  # 점수 저장 시간

    user = relationship("User", back_populates="scores")  # User 테이블과 연결
from sqlalchemy import Column, Integer, String
from ..database import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)  # 기본 키
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)

from sqlalchemy import Column, Integer, String
from ..core.database import Base

class Quiz(Base):
    """ 퀴즈(Quiz) 테이블 정의 """

    __tablename__ = "quizzes"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    explanation = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    category = Column(String, nullable=False)

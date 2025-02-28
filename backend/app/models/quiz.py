from sqlalchemy import Column, Integer, String
from ..database import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    explanation = Column(String, nullable=True)
    answer = Column(String, nullable=False)


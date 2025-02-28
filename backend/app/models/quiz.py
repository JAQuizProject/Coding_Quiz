from sqlalchemy import Column, Integer, String
from ..core.database import Base

class Quiz(Base):
    """ 퀴즈(Quiz) 테이블 정의 """

    # 테이블 이름 설정
    __tablename__ = "quizzes"
    # 기존 테이블이 이미 존재하면 덮어쓰도록 설정
    __table_args__ = {'extend_existing': True}

    # 기본 키 (id) - 각 퀴즈를 식별하는 고유한 값
    id = Column(Integer, primary_key=True, index=True)
    # 퀴즈 질문
    question = Column(String, nullable=False)
    # 질문에 대한 설명 또는 해설
    explanation = Column(String, nullable=True)
    # 퀴즈 정답
    answer = Column(String, nullable=False)

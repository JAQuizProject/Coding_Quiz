from sqlalchemy import Column, Integer, String
from ..database import Base

class User(Base):
    """
    사용자(User) 테이블 정의
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # 기본 키 (AUTO_INCREMENT)
    username = Column(String, unique=True, index=True, nullable=False)  # 유저네임
    email = Column(String, unique=True, index=True, nullable=False)  # 이메일
    password = Column(String, nullable=False)

from sqlalchemy import Column, Integer, String
from backend.app.database import Base

class User(Base):
    """
    사용자(User) 테이블 정의
    - Java의 @Entity와 유사
    - Java JDBC에서는 'users' 테이블을 직접 생성해야 함
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # 기본 키 (AUTO_INCREMENT)
    username = Column(String, unique=True, index=True, nullable=False)  # 유저네임 (고유)
    email = Column(String, unique=True, index=True, nullable=False)  # 이메일 (고유)
    password = Column(String, nullable=False)  # 비밀번호 

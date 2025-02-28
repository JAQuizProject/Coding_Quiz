from sqlalchemy import Column, Integer, String
from ..core.database import Base

class User(Base):
    """사용자(User) 테이블 정의"""

    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # 해싱된 비밀번호 저장

    def set_password(self, password: str):
        """비밀번호를 해싱하여 저장"""
        from ..core.security import get_password_hash  # 🔥 여기서만 import
        self.hashed_password = get_password_hash(password)

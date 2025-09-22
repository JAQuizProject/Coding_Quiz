# ...existing code...
from sqlalchemy.orm import Session


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str):
        from ..models.user import User

        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str):
        from ..models.user import User

        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, username: str, email: str, hashed_password: str):
        from ..models.user import User

        new_user = User(username=username, email=email, hashed_password=hashed_password)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

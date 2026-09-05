from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models import User


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, email: str, password: str) -> User:
        existing = self.db.scalar(select(User).where(User.email == email.lower()))
        if existing:
            raise ValueError("A user with this email already exists.")

        user = User(email=email.lower(), password_hash=hash_password(password))
        self.db.add(user)
        self.db.flush()
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = self.db.scalar(select(User).where(User.email == email.lower()))
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password.")
        return user

    def create_token(self, user: User) -> str:
        return create_access_token(user.id)

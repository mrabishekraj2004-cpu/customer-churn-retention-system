from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import User, UserRole


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        normalized_email = email.strip().lower()

        statement = select(User).where(
            User.email == normalized_email
        )

        return self.db.scalar(statement)

    def create(
        self,
        *,
        email: str,
        password_hash: str,
        role: UserRole,
    ) -> User:
        normalized_email = email.strip().lower()

        user = User(
            email=normalized_email,
            password_hash=password_hash,
            role=role.value,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def set_active(
        self,
        user: User,
        *,
        is_active: bool,
    ) -> User:
        user.is_active = is_active

        self.db.commit()
        self.db.refresh(user)

        return user

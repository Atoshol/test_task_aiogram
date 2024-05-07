from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, JSON, String,
    asc, func, select, and_, delete, desc, Boolean, update
)
from sqlalchemy.exc import IntegrityError

from db.postgres import Base
from decorators.db_session import db_session


class UserModel(BaseModel):
    user_id: int
    username: str
    first_name: str
    last_name: str = None
    language_code: str = None


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, index=True, primary_key=True)
    username = Column(String, index=True, nullable=True)
    first_name = Column(String, index=True)
    last_name = Column(String, nullable=True)
    language_code = Column(String, default="en")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserStore:
    @staticmethod
    @db_session
    async def create_user(session, data: dict):
        user_id = data["user_id"]
        existing_user = await UserStore.get_user_by_id(user_id)

        if existing_user:
            return None

        new_user = User(
            user_id=user_id,
            username=data["username"],
            first_name=data["first_name"],
            last_name=data.get("last_name"),
        )

        try:
            session.add(new_user)
            await session.commit()
            return new_user
        except IntegrityError:
            # Handle integrity error, e.g., duplicate key violation
            session.rollback()
            return None

    @staticmethod
    @db_session
    async def get_user_by_id(session, user_id: int) -> Optional[User]:
        result = await session.execute(select(User).filter(User.user_id == user_id))
        user = result.scalar_one_or_none()
        return user

    @staticmethod
    @db_session
    async def update_user(session, user_id: int, data: dict) -> Optional[UserModel]:
        # Retrieve the user profile based on the user_id
        user = await session.execute(select(User).filter(User.user_id == user_id))
        user_data = user.scalar_one_or_none()

        if user_data:
            # Update the user profile with the provided changes
            for key, value in data.items():
                setattr(user_data, key, value)

            # Update the 'updated_at' field to reflect the latest modification time
            user_data.updated_at = func.now()

            # Commit the changes to the database
            await session.commit()

            # Return the updated user profile
            updated_profile_dict = {
                "user_id": user_data.user_id,
                "username": str(user_data.username),
                "language_code": user_data.language_code,
                "first_name": str(user_data.first_name),
                "last_name": str(user_data.last_name)
            }
            return UserModel(**updated_profile_dict)

        return None

    @staticmethod
    @db_session
    async def delete_user(session, user_id: int) -> bool:
        user = await UserStore.get_user_by_id(user_id)
        if user:
            session.delete(user)
            await session.commit()
            return True
        return False

    @staticmethod
    @db_session
    async def set_user_language_code(session, user_id: int, language_code: str) -> Optional[User]:
        user = await UserStore.get_user_by_id(user_id)
        if user:
            user.language_code = language_code
            await session.commit()
        return user

    @staticmethod
    @db_session
    async def get_user_language_code(session, user_id: int) -> Optional[str]:
        user = await UserStore.get_user_by_id(user_id)
        return user.language_code if user else None
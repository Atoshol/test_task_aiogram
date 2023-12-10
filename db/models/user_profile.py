from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, JSON, String,
                        and_, asc, delete, desc, func, select, update)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship

from db.postgres import Base
from decorators.db_session import db_session



class UserProfileModel(BaseModel):
    id: int
    user_id: int
    address: str
    account_id: str


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    address = Column(String, nullable=True)
    account_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserProfileStore:
    @staticmethod
    @db_session
    async def create_user_profile(session, data: dict):
        user_id = data["user_id"]

        new_user = UserProfile(
            user_id=user_id,
            address=data["address"],
            account_id=data["account_id"],
        )

        session.add(new_user)
        await session.commit()
        return new_user

    @staticmethod
    @db_session
    async def get_user_profile(session, user_id: int) -> Optional[UserProfileModel]:
        result = await session.execute(select(UserProfile).filter(UserProfile.user_id == user_id))
        profile = result.scalar_one_or_none()

        if profile:
            profile_dict = {
                "id": profile.id,
                "user_id": profile.user_id,
                "address": profile.address,
                "account_id": profile.account_id,
            }
            return UserProfileModel(**profile_dict)

        return None

    @staticmethod
    @db_session
    async def update_user_profile(session, user_id: int, updates: dict) -> Optional[UserProfileModel]:
        # Retrieve the user profile based on the user_id
        user_profile = await session.execute(select(UserProfile).filter(UserProfile.user_id == user_id))
        profile = user_profile.scalar_one_or_none()

        if profile:
            # Update the user profile with the provided changes
            for key, value in updates.items():
                setattr(profile, key, value)

            # Update the 'updated_at' field to reflect the latest modification time
            profile.updated_at = func.now()

            # Commit the changes to the database
            await session.commit()

            # Return the updated user profile
            updated_profile_dict = {
                "id": profile.id,
                "user_id": profile.user_id,
                "address": profile.address,
                "account_id": profile.account_id,
            }
            return UserProfileModel(**updated_profile_dict)

        return None

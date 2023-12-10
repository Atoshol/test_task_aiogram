from functools import wraps
from db.postgres import async_session
from sqlalchemy.exc import SQLAlchemyError


def db_session(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            try:
                return await func(session, *args, **kwargs)

            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    return wrapper

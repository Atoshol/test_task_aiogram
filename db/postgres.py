from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from utils.defaults import DB_URL

Base = declarative_base()

engine = create_async_engine(DB_URL, echo=False)  # Set echo to False
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

import asyncio
from sqlalchemy import text
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.asyncio import create_async_engine

from utils.defaults import DB_URL
from db.postgres import Base, engine
from db.models.user import User  # don't remove this import
from db.models.user_profile import UserProfile  # don't remove this import


async def remove_all_tables():
    async with engine.begin() as connection:
        remove_all = text('''
        DO $$ DECLARE
            r RECORD;
        BEGIN
            -- if the schema you operate on is not "current", you will want to
            -- replace current_schema() in query with 'schematodeletetablesfrom'
            -- *and* update the generate 'DROP...' accordingly.
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
        ''')
        await connection.execute(remove_all)


async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def recreate_tables():
    await remove_all_tables()
    await create_tables()


asyncio.run(recreate_tables())

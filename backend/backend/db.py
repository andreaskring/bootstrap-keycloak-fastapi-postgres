from sqlalchemy import create_engine
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import declarative_base

from backend.config import Settings


Base = declarative_base()


def get_db_url(settings: Settings) -> str:
    return (
        f"postgresql+psycopg://"
        f"{settings.db_user}:{settings.db_password.get_secret_value()}"
        f"@{settings.db_host}/{settings.db_name}"
    )


def get_engine(settings: Settings) -> Engine:
    return create_engine(get_db_url(settings))


def get_async_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(get_db_url(settings))

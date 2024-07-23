from functools import cache

from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import declarative_base
from sqlalchemy.util import FacadeDict

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


@cache
def get_tables(engine: Engine) -> FacadeDict[str, Table]:
    """
    Get the DB tables.

    Args:
        engine: the SQLAlchemy engine to use

    Returns:
         A dictionary-like object containing the DB tables.
    """
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)
    return metadata_obj.tables

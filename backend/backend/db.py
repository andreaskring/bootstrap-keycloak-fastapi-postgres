from sqlalchemy import create_engine
from sqlalchemy import Engine


def get_db_url(settings: Settings) -> str:
    return f"postgresql+psycopg2://{settings.db_user}:{settings.db_password.get_secret_value()}@{settings.db_host}/{settings.db_name}"


def get_engine(settings: SDToolPlusSettings) -> Engine:
    return create_engine(get_db_url(settings))
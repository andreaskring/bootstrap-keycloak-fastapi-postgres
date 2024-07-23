from pydantic import PositiveInt, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str
    db_port: PositiveInt
    db_name: str
    db_user: str
    db_password: SecretStr


def get_settings(*args, **kwargs) -> Settings:
    return Settings(*args, **kwargs)

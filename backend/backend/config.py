from pydantic import PositiveInt, SecretStr, AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str
    db_port: PositiveInt
    db_name: str
    db_user: str
    db_password: SecretStr

    auth_host: str
    auth_port: PositiveInt
    auth_realm: str
    auth_http_schema: str = "https"


def get_settings(*args, **kwargs) -> Settings:
    return Settings(*args, **kwargs)

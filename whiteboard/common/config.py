import logging
import os
from typing import Dict, Type

class BaseConfig:
    Testing = False
    SQLALCHEMY_DATABASE_URI =(
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_SERVER')}:{os.getenv('POSTGRES_PORT', 5432)}"
        f"/{os.getenv('POSTGRES_DB')}"
    )
    # loglevel DEBUG is 10
    LOG_LEVEL = int(os.getenv("LOG_LEVEL", 10))
    ENV = os.getenv("ENV", "dev")


class TestConfig(BaseConfig):
    # loglevel 10 is info
    LOG_LEVEL = 10
    # for docker services, use db, test-db and may run different container from postgres:14-alpine image
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://"
        f"{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_TEST_SERVER')}:{os.getenv('POSTGRES_PORT')}"
        f"/{os.getenv('POSTGRES_DB')}"
    )
    TESTING = True
    ORSTORE_URL = os.getenv("ORSTORE_URL")
    RETRY_LIMIT = 1


class Config(BaseConfig):
    LOG_LEVEL = 20


class DevConfig(BaseConfig):
    LOG_LEVEL = 10

_config_mapping: Dict[str, Type[BaseConfig]] = {
    "test": TestConfig,
    "dev": DevConfig,
    "prod": Config
}


def get_current_config() -> Type[BaseConfig]:
    current_env = os.getenv("APP_SETTINGS", "dev")
    config = _config_mapping.get(current_env, DevConfig)
    return config

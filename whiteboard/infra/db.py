from sqlalchemy import create_engine
from sqlalchemy.orm import Session as sqlalchemySession
from sqlalchemy.orm import sessionmaker
from common.config import get_current_config, Config
from typing import Optional


class SessionContextManager:
    def __init__(self, config: Optional[Config] = get_current_config()) -> None:
        self._engine = create_engine(
            # enable the connection pool
            config.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True
        )
        self._session_maker = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

    def __enter__(self, *args, **kwargs) -> sqlalchemySession:
        self._session = self._session_maker()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()


def get_session(config: Optional[Config] = get_current_config()):
    with SessionContextManager(config) as session:
        yield session

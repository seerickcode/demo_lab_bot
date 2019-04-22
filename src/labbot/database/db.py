import logging
import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from alembic.config import Config
from alembic import command

__all__ = ["DB", "DeclarativeBase"]

logger = logging.getLogger(__name__)

DeclarativeBase = declarative_base()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DB(object, metaclass=Singleton):
    """
    Singleton to hold / manage the database connections
    """

    def __init__(self, db_url=None):
        self.db_url = (
            db_url if db_url else os.getenv("LABBOT_DB_URL", "sqlite:///labbot.db")
        )
        self.engine = create_engine(self.db_url, pool_recycle=3600)
        self.Session = sessionmaker(bind=self.engine)
        DeclarativeBase.metadata.create_all(self.engine)
        # alembic_cfg = Config("alembic.ini")
        # command.stamp(alembic_cfg, "head")

    @contextmanager
    def session(self):
        _session = self.Session()
        try:
            yield _session
            _session.commit()
        except Exception:
            _session.rollback()
            raise
        finally:
            _session.close()

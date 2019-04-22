import enum
import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Sequence,
    Boolean,
    Binary,
    DateTime,
    Enum,
)
from .db import DeclarativeBase

__all__ = ["Lab", "LabStatus"]


class LabStatus(enum.Enum):
    UNKNOWN = 0
    PENDING = 10
    WAITING_INSTANCE = 20
    WAITING_DNS = 30
    WAITING_HEALTH = 35
    ACTIVE = 40
    DEACTIVATE_DNS = 50
    DEACTIVATE_INSTANCE = 60
    TERMINATED = 70


class Lab(DeclarativeBase):
    __tablename__ = "labs"

    id = Column(Integer, Sequence("file_id_seq"), primary_key=True)
    slack_owner_id = Column(String(22))
    url = Column(String(255))
    ip = Column(String(16))
    do_reference = Column(String(255))
    cf_reference = Column(String(255))
    active = Column(Boolean, default=True)
    status = Column(Enum(LabStatus), default=LabStatus.UNKNOWN)
    ts_created = Column(DateTime, default=datetime.datetime.now)
    ts_updated = Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return f"<Lab({self.id}:{self.slack_owner_id} {self.ip} {self.url})"

from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Boolean, DATETIME, Nullable, BigInteger
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.dialects.postgresql import TIMESTAMP as PgTime
from sqlalchemy.dialects.postgresql import DATE as PgDate
import os

from const.event_status import EventStatus
from const.priority_status import PriorityStatus
from const.repeatable_type import RepeatType

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(30), nullable=False)

class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    title = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(PgEnum(EventStatus, name='event_status_enum', create_type=False), nullable=False, default=EventStatus.TO_DO)
    priority = Column(PgEnum(PriorityStatus, name='priority_status_enum', create_type=False), nullable=False, default=PriorityStatus.MEDIUM)
    created_at = Column(PgDate, nullable=False, default=datetime.now())
    updated_at = Column(PgDate, nullable=False, default=datetime.now)
    repeatable = Column(Boolean, nullable=False, default=False)
    remind_at = Column(PgTime, nullable=False, default=datetime.now())
    repeat_type = Column(PgEnum(RepeatType, name='repeat_type_enum', create_type=False), nullable=False, default=RepeatType.EVERY_DAY)
    chat_name = Column(String(10), nullable=True, default=None)
    telegram_chat_id = Column(BigInteger, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

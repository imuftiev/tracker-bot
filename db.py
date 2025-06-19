from datetime import datetime, time

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Boolean, BigInteger, Time, text, ARRAY
from sqlalchemy.orm import declarative_base, relationship
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy import DateTime
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
    events = relationship("Event", back_populates="user")

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(PgEnum(EventStatus, name='event_status_enum', create_type=False), nullable=False,
                    default=EventStatus.TO_DO)
    priority = Column(PgEnum(PriorityStatus, name='priority_status_enum', create_type=False), nullable=False,
                      default=PriorityStatus.MEDIUM)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now)
    repeatable = Column(Boolean, nullable=False, default=False)
    sent = Column(Boolean, nullable=False, default=False)
    remind_at = Column(DateTime, nullable=False, default=datetime.now)
    remind_time = Column(
        Time,
        nullable=False,
        server_default=text("'08:00:00'")
    )
    repeat_type = Column(PgEnum(RepeatType, name='repeat_type_enum', create_type=False), nullable=False,
                         default=RepeatType.ONLY_DAY)
    days_of_week = Column(ARRAY(String))
    chat_name = Column(String(10), nullable=True, default=None)
    telegram_chat_id = Column(BigInteger, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="events")

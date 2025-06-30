from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Boolean, BigInteger, Time, text, ARRAY
from sqlalchemy.orm import declarative_base, relationship
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy import DateTime
import os

from const.event.status import Status
from const.event.priority import Priority
from const.event.repeatable import RepeatType

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(30), nullable=False)

    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    groups = relationship("Group", back_populates="user", cascade="all, delete-orphan")


class Group(Base):
    __tablename__ = "groups"


    def __str__(self):
        return (
            f"🟢 {self.name}"
        )

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    telegram_group_id = Column(BigInteger, unique=False, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="groups")
    events = relationship("Event", back_populates="group", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = 'events'

    def __str__(self):
        return (
            f"<b>📎 Событие: </b><code><u>{self.id}</u></code>\n"
            f"<b>🔔 Название:</b> <u>{self.title}</u>\n"
            f"<b>📝 Описание:</b> <u>{self.description or ''}</u>\n"
            f"<b>📌 Статус:</b> <u>{self.status.value}</u>\n"
            f"<b>⚡ Приоритет:</b> <u>{self.priority.value}</u>\n"
            f"<b>📆 Тип напоминания:</b> <u>{self.repeat_type.value}</u>\n"
            f"<b>⏰ Напоминать в:</b> <u>{self.remind_at}</u>.\n"
            f"<b>Дни:</b> {self.days_of_week or ''} {self.days_of_month or ''}\n"
        )

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(PgEnum(Status, name='status_enum', create_type=False), nullable=False,
                    default=Status.TO_DO)
    priority = Column(PgEnum(Priority, name='priority_enum', create_type=False), nullable=False,
                      default=Priority.MEDIUM)
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
    days_of_month = Column(ARRAY(Integer))
    month = Column(ARRAY(Integer), nullable=True)
    chat_type = Column(String(10), nullable=True, default=None)
    telegram_chat_id = Column(BigInteger, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="events")
    group = relationship("Group", back_populates="events")

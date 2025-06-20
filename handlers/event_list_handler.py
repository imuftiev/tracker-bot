from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker

from config import BotConfig
from db import engine, Event

config = BotConfig()
router = Router()
Session = sessionmaker(bind=engine)

@router.message(StateFilter(None), Command("list"))
async def event_list_handler(message: Message):
    with Session() as session:
        event_list = session.query(Event).filter_by(telegram_chat_id=message.from_user.id).all()
        for event in event_list:
            await message.answer(text=(f"🔔<strong> Событие: </strong> <i>{event.title}</i>\n"
                              f"📝<strong> Описание: </strong> <i>{event.description}</i>\n"
                              f"❓<strong> Статус: </strong> <i>{event.status.value}</i>\n"
                              f"✔️<strong> Приоритет: </strong> <i>{event.priority.value}</i>\n"),)
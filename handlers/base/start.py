import logging

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from config import BotConfig
from sqlalchemy.orm import sessionmaker

from db import engine, User, Event

config = BotConfig()
router = Router()
Session = sessionmaker(bind=engine)


@router.message(Command("start"))
async def cmd_start(message: Message):
    with Session() as session:
        try:
            if (session.query(User).filter_by(telegram_user_id=message.from_user.id).first()
                    or session.query(Event).filter_by(telegram_chat_id=message.chat.id).first()):
                await message.answer(config.start_text_user)
            else:
                new_user = User(telegram_user_id=message.from_user.id, username=message.from_user.username)
                session.add(new_user)
                session.commit()
                await message.answer(config.start_text, parse_mode=ParseMode.HTML)
        except Exception as e:
            logging.error(e)

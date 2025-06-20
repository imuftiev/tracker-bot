import logging

from aiogram.types import Message
from aiogram.filters import Command

from aiogram import Router
from sqlalchemy.orm import sessionmaker

from config import BotConfig
from db import engine

config = BotConfig()
router = Router()
Session = sessionmaker(bind=engine)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    try:
        await message.answer(config.help_text)
    except Exception as e:
        logging.error(e)

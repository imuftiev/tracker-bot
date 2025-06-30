import logging

from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command

from aiogram import Router
from sqlalchemy.orm import sessionmaker

from config import BotConfig
from db import engine

config = BotConfig()
router = Router()
Session = sessionmaker(bind=engine)

"""
    Обработчик команды /help
"""


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    try:
        await message.answer(text=config.assembled_text, parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(e)

from aiogram import Router
from aiogram import F
from aiogram.types import Message

from config import BotConfig
from handlers.filter.filter import IsPrivate

router = Router()
config = BotConfig()


@router.message(F.text)
async def default_message_handler(message: Message):
    await message.answer(text=config.default_text)

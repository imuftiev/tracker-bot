from aiogram import Router
from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message

from config import BotConfig

router = Router()
config = BotConfig()


@router.message(Command("id"))
async def get_group_id_handler(message: Message):
    await message.answer(text=f"ℹ️ <b>ID</b> этого чата: {str(message.chat.id)}")


@router.message(F.text)
async def default_message_handler(message: Message):
    await message.answer(text=config.default_text)

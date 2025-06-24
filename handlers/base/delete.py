import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import sessionmaker

from const.event.delete import DeleteEvent
from db import Event, engine
from handlers.filter.filter import IsPrivate
from keyboards.keyboards import delete_type_inline_kb
from aiogram import F
from config import BotConfig

config = BotConfig()
router = Router()
Session = sessionmaker(bind=engine)


@router.message(Command("delete"), IsPrivate())
async def delete_events(message: Message):
    await message.answer(text="Как удалить ивенты", reply_markup=delete_type_inline_kb())


@router.callback_query(F.data == DeleteEvent.DELETE_ALL.value)
async def delete_all_events(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    try:
        with Session() as session:
            events = session.query(Event).filter_by(telegram_chat_id=chat_id).all()
            if not events:
                await callback.message.answer(text=config.delete_list_empty)
                return
            for event in events:
                session.delete(event)
            session.commit()
        await callback.message.answer(text=config.delete_all_text)
    except Exception as error:
        logging.error(error)

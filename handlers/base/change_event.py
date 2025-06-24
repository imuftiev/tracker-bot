import logging

from aiogram.filters import Command

from aiogram import Router
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker

from db import engine, Event

router = Router()
Session = sessionmaker(bind=engine)


@router.message(Command("change"))
async def change_event(message : Message):
    try:
        chat_id = message.chat.id
        with Session() as session:
            events = session.query(Event).filter_by(telegram_chat_id=chat_id).all()
            for event in events:
                await message.answer(text=str(event))
        await message.answer(text="Какое событие хотите изменить")
    except Exception as error:
        logging.error(error)
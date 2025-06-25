import logging
import re

from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.orm import sessionmaker

from db import engine, Event

router = Router()
Session = sessionmaker(bind=engine)


@router.callback_query(F.data.startswith("update_event:"))
async def update_event_handler(callback: CallbackQuery, state : FSMContext):
    try:
        match = re.match(r"update_event:(\d+)", callback.data)
        if not match:
            await callback.message.answer("Неверный формат команды удаления.")
            return

        event_id = int(match.group(1))

        with Session() as session:
            event = session.query(Event).filter_by(id=event_id).first()
            if not event:
                await callback.message.answer("Событие не найдено.")
                return

            session.commit()

        await callback.message.edit_text("🔄️ Событие успешно изменено.", reply_markup=None)

    except Exception as e:
        logging.error(e)
        await callback.message.answer("Ошибка при удалении события.")
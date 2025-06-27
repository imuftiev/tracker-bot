import logging
import re
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import sessionmaker
from apscheduler.jobstores.base import JobLookupError
from scheduler.apscheduler import scheduler


from const.callback.delete import DeleteEvent
from db import Event, engine
from handlers.filter.filter import IsPrivate
from keyboards.keyboards import get_delete_type_keyboard
from aiogram import F
from config import BotConfig

config = BotConfig()
router = Router()
Session = sessionmaker(bind=engine)

"""
    Обработчик команды /delete
"""
@router.message(Command("delete"), IsPrivate())
async def delete_command(message: Message):
    await message.answer(text="Удалить все ивенты. Для удаления отдельных введите команду /list -> 'Все'", reply_markup=get_delete_type_keyboard())


"""
    Обработчик callback-кнопки удалить 'Все' ивенты
"""
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
                remove_scheduler_jobs(event.id)
                session.delete(event)
            session.commit()

        await callback.message.answer(text=config.delete_all_text)

    except Exception as error:
        logging.error(error)


"""
    Обработчик callback-кнопки 'delete' у каждого отдельного ивента в списке
"""
@router.callback_query(F.data.startswith("delete_event:"))
async def delete_event_by_id(callback: CallbackQuery):
    try:
        match = re.match(r"delete_event:(\d+)", callback.data)
        if not match:
            await callback.message.answer("Неверный формат команды удаления.")
            return

        event_id = int(match.group(1))

        with Session() as session:
            event = session.query(Event).filter_by(id=event_id).first()
            if not event:
                await callback.message.answer("Событие не найдено или уже удалено.")
                return

            session.delete(event)
            session.commit()

        remove_scheduler_jobs(event_id)

        await callback.message.edit_text("🗑️ Событие успешно удалено.", reply_markup=None)

    except Exception as e:
        logging.error(e)
        await callback.message.answer("Ошибка при удалении события.")


def remove_scheduler_jobs(event_id: int):
    try:
        scheduler.remove_job(f"event_{event_id}")
    except JobLookupError:
        pass

    for suffix in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', '*']:
        try:
            scheduler.remove_job(f"event_{event_id}_{suffix}")
        except JobLookupError:
            continue


import logging
import re
from datetime import datetime

from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import sessionmaker

from bot_state.states import UpdateEventState
from const.callback.callback_types import InlineButtonType
from const.event.priority import Priority
from const.event.status import Status
from db import engine, Event
from handlers.base.add import push_state
from keyboards import keyboards
from keyboards.keyboards import update_event_keyboard, get_event_action_keyboard

router = Router()
Session = sessionmaker(bind=engine)


@router.callback_query(F.data.startswith("update_event:"))
async def update_handler(callback: CallbackQuery, state: FSMContext):
    try:
        match = re.match(r"update_event:(\d+)", callback.data)
        event_id = int(match.group(1))
        with Session() as session:
            event = session.query(Event).filter_by(id=event_id).first()
            if not event:
                await callback.message.answer("Событие не найдено или уже удалено.")
                return
        await push_state(state, UpdateEventState.updating)
        await callback.message.edit_text(
            text="Что изменить в событии",
            reply_markup=update_event_keyboard(event_id)
        )
    except Exception as e:
        logging.error(e)
        await callback.message.answer("Ошибка при редактировании события.")


@router.callback_query(F.data.startswith("update_description:"))
async def update_event_description(callback: CallbackQuery, state: FSMContext):
    try:
        match = re.match(r"update_description:(\d+)", callback.data)
        if not match:
            await callback.message.answer("Некорректный callback.")
            return

        event_id = int(match.group(1))

        await state.update_data(event_id=event_id)
        await callback.message.edit_text("Введите новое описание:", reply_markup=keyboards.get_cancel_return_keyboard())
        await push_state(state, UpdateEventState.updating_description)

    except Exception as e:
        logging.error(e)
        await callback.message.answer("Ошибка при изменении описания.")


@router.callback_query(F.data.startswith("update_status:"))
async def update_event_status(callback: CallbackQuery, state: FSMContext):
    try:
        match = re.match(r"update_status:(\d+)", callback.data)
        if not match:
            await callback.message.answer("Неверный формат callback.")
            return

        event_id = int(match.group(1))
        await push_state(state, UpdateEventState.updating_status)
        await state.update_data(event_id=event_id)

        await callback.message.edit_text("На какой статус изменить", reply_markup=keyboards.get_status_keyboard())

    except Exception as e:
        logging.error(e)
        await callback.message.answer("Ошибка при обновлении статуса.")


@router.callback_query(F.data.startswith("update_priority:"))
async def update_event_priority(callback: CallbackQuery, state: FSMContext):
    try:
        match = re.match(r"update_priority:(\d+)", callback.data)
        if not match:
            await callback.message.answer("Неверный формат callback.")
            return
        event_id = int(match.group(1))
        await push_state(state, UpdateEventState.updating_priority)
        await state.update_data(event_id=event_id)
        await callback.message.edit_text("На какой приоритет изменить", reply_markup=keyboards.get_priority_keyboard())
    except Exception as e:
        logging.error(e)
        await callback.message.answer("Ошибка при обновлении приоритета.")


@router.callback_query(
    F.data.in_([p.value for p in Priority] + [InlineButtonType.CANCEL.value, InlineButtonType.RETURN.value]),
    UpdateEventState.updating_priority
)
async def process_new_priority(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        event_id = data.get("event_id")
        with Session() as session:
            event = session.query(Event).filter_by(id=event_id).first()
            if not event:
                logging.error(f"Event с таким {event_id} не найден")
            event.priority = Priority(callback.data)
            event.updated_at = datetime.now()
            session.commit()
            await callback.message.edit_text(f"<b>Приоритет</b> {event_id} события <b>обновлен</b> ✅")
        await state.clear()
    except Exception as e:
        logging.error(e)


@router.callback_query(
    F.data.in_([s.value for s in Status] + [InlineButtonType.CANCEL.value, InlineButtonType.RETURN.value]),
    UpdateEventState.updating_status
)
async def process_new_status(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        event_id = data.get("event_id")
        with Session() as session:
            event = session.query(Event).filter_by(id=event_id).first()
            if not event:
                logging.error(f"Event с таким {event_id} не найден")
            event.status = Status(callback.data)
            event.updated_at = datetime.now()
            session.commit()
            await callback.message.edit_text(f"<b>Статус</b> {event_id} события <b>обновлен</b> ✅")
        await state.clear()
    except Exception as e:
        logging.error(e)


@router.message(UpdateEventState.updating_description)
async def process_new_description(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        event_id = data.get("event_id")

        new_description = message.text.strip()

        with Session() as session:
            event = session.query(Event).filter_by(id=event_id).first()
            if not event:
                await message.answer("Событие не найдено.")
                return

            event.description = new_description
            event.updated_at = datetime.now()
            session.commit()

        await message.answer(f"<b>Описание</b> {event_id} события <b>обновлен</b> ✅")
        await state.clear()
    except Exception as e:
        logging.error(e)


@router.callback_query(F.data.startswith("return_to_event:"))
async def return_to_event_handler(callback: CallbackQuery):
    try:
        match = re.match(r"return_to_event:(\d+)", callback.data)
        event_id = int(match.group(1))
        with Session() as session:
            event = session.query(Event).filter_by(id=event_id).first()
            if not event:
                await callback.message.edit_text("Событие не найдено.")
                return
        await callback.message.edit_text(str(event), parse_mode="HTML",
                                         reply_markup=get_event_action_keyboard(event_id))
    except Exception as e:
        logging.error(e)
        await callback.message.answer("Ошибка при возврате к событию.")

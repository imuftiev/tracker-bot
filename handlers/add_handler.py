import logging
from datetime import datetime, timedelta

from aiogram import types
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import sessionmaker
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from const.event_status import EventStatus
from const.priority_status import PriorityStatus
from keyboards import for_event_type
from aiogram import F

from bot_state.add_event_state import AddEventState
from config import BotConfig
from db import Event, engine, User
from keyboards.for_event_type import cancel_button

config = BotConfig()
router = Router()
Session = sessionmaker(bind=engine)
new_event = Event()


@router.message(StateFilter(None), Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    try:
        new_event.telegram_chat_id = message.chat.id
        await state.set_state(AddEventState.adding_title)
        await message.answer(
            text="Введите название события", parse_mode=ParseMode.HTML, reply_markup=cancel_button()
        )
    except Exception as e:
        logging.error(e)


@router.message(AddEventState.adding_title, F.text)
async def event_title(message: Message, state: FSMContext):
    try:
        await state.set_state(AddEventState.adding_description)
        new_event.title = message.text
        await message.answer(
            text="Введите описание события", reply_markup=cancel_button()
        )
    except Exception as e:
        logging.error(e)


@router.message(F.text, AddEventState.adding_description)
async def event_description(message: Message, state: FSMContext):
    try:
        await state.set_state(AddEventState.adding_status)
        new_event.description = message.text
        await message.answer(
            text="Выберите статус события", reply_markup=for_event_type.status_inline_kb()
        )
    except Exception as e:
        logging.error(e)


@router.callback_query(F.data, AddEventState.adding_status)
async def event_status(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.set_state(AddEventState.adding_repeatable)
        new_event.status = EventStatus(callback.data)
        await callback.message.answer(text="Выберите когда напомнить про событие",
                                      reply_markup=for_event_type.repeatable_inline_kb())
    except Exception as e:
        logging.error(e)


@router.callback_query(F.data, AddEventState.adding_repeatable)
async def event_repeatable(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.set_state(AddEventState.adding_remind_at)
        new_event.repeat_type = callback.data.__str__()
        await callback.message.answer(text="Напишите время напоминания в формате 'HH:MM'")
    except Exception as e:
        logging.error(e)


@router.message(F.text, AddEventState.adding_remind_at)
async def event_remind_at(message: Message, state: FSMContext):
    try:
        await state.set_state(AddEventState.adding_priority)
        time_input = message.text.strip()
        time = datetime.strptime(time_input, "%H:%M").time()
        now = datetime.now()
        remind_time = datetime.combine(now.date(), time)
        if remind_time < now:
            remind_time += timedelta(days=1)

        new_event.remind_at = remind_time
        await message.answer(text="Выберите приоритет события",
                             reply_markup=for_event_type.priority_inline_kb())
    except Exception as e:
        logging.error(e)


@router.callback_query(F.data, AddEventState.adding_priority)
async def event_priority(callback: types.CallbackQuery, state: FSMContext):
    with Session() as session:
        try:
            new_event.priority = PriorityStatus(callback.data)
            new_event.user_id = session.query(User).filter_by(telegram_user_id=callback.from_user.id).first().id
            session.add(new_event)
            session.commit()
            await state.set_data({})
        except Exception as e:
            logging.error(e)


@router.callback_query(F.data == 'cancel')
async def cancel_event(message: Message, state: FSMContext):
    with Session() as session:
        session.flush()
        await state.clear()
        await message.answer(text="Действие добавления отменено!")

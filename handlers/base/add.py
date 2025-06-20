import logging
from datetime import datetime, timedelta

from aiogram import types
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import sessionmaker
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from handlers.keyboard.inline import back
from handlers.reminders.time import set_time_remind

from const.event.status import Status
from const.event.priority import Priority
from const.event.repeatable import RepeatType, RepeatDays
from keyboards import keyboards
from aiogram import F

from bot_state.states import AddEventState, RepeatableEventState
from config import BotConfig
from db import Event, engine, User
from keyboards.keyboards import cancel_button, cancel_back_button

config = BotConfig()
router = Router()
Session = sessionmaker(bind=engine)
new_event = Event()

"""
    Для реализации возможности диалога с ботом и сохранением его состояния был использован 
    принцип Конечного Автомата с применением FSMContext
    Инициализация начального состояния происходит путем ввода команды – /add
    Сброс состояния бота – /cancel
"""


async def push_state(state: FSMContext, new_state):
    data = await state.get_data()
    history = data.get("history", [])
    current_state = await state.get_state()
    if current_state:
        history.append(current_state)
    await state.update_data(history=history)
    await state.set_state(new_state)


""" Обработчик команды /add """


@router.message(StateFilter(None), Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    try:
        new_event.telegram_chat_id = message.chat.id
        await push_state(state, AddEventState.adding_title)
        await message.answer(
            text="Введите название события", parse_mode=ParseMode.HTML, reply_markup=keyboards.cancel_button()
        )
    except Exception as e:
        logging.error(e)


""" Обработчик сообщения – Название ивента"""


@router.message(AddEventState.adding_title, F.text)
async def event_title(message: Message, state: FSMContext):
    try:
        await push_state(state, AddEventState.adding_description)
        new_event.title = message.text
        await message.answer(
            text="Введите описание события", reply_markup=cancel_back_button()
        )
    except Exception as e:
        logging.error(e)


""" Обработчик сообщения – Описание ивента"""


@router.message(F.text, AddEventState.adding_description)
async def event_description(message: Message, state: FSMContext):
    try:
        await push_state(state, AddEventState.adding_status)
        new_event.description = message.text
        await message.answer(
            text="Выберите статус события", reply_markup=keyboards.status_inline_kb()
        )
    except Exception as e:
        logging.error(e)


""" Обработчик Callback вызова – Статус ивента"""


@router.callback_query(F.data, AddEventState.adding_status)
async def event_status(callback: types.CallbackQuery, state: FSMContext):
    try:
        if callback.data == "cancel":
            await cancel_button(callback, state)
            return
        if callback.data == "back":
            await back(callback, state)
            return

        await push_state(state, AddEventState.adding_repeatable)
        new_event.status = Status(callback.data)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            text="Когда напомнить про событие",
            reply_markup=keyboards.repeatable_inline_kb()
        )
    except Exception as e:
        logging.error(f"Ошибка в event_status: {e}")


""" Обработчик Callback вызова – Когда напоминать про событие"""


@router.callback_query(F.data, AddEventState.adding_repeatable)
async def event_repeatable(callback: types.CallbackQuery, state: FSMContext):
    try:
        if callback.data == "cancel":
            await cancel_button(callback, state)
            return
        if callback.data == "back":
            await back(callback, state)
            return

        new_event.repeat_type = RepeatType(callback.data)
        new_event.repeatable = True
        await push_state(state, AddEventState.adding_remind_at)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Напишите время напоминания в формате '12:30' или '1230'")
    except Exception as e:
        logging.error(f"Ошибка в event_repeatable: {e}")


""" Обработчик сообщения – Время напоминания 'HH:MM' """


@router.message(F.text, AddEventState.adding_remind_at)
async def event_remind_at(message: Message, state: FSMContext):
    try:
        now = datetime.now()
        remind_time = await set_time_remind(message, state)
        if remind_time is None:
            return
        if remind_time < now:
            remind_time += timedelta(days=1)
        new_event.remind_at = remind_time
        await push_state(state, AddEventState.adding_priority)
        await message.answer(text="Приоритет события",
                             reply_markup=keyboards.priority_inline_kb())
    except Exception as e:
        logging.error(e)


@router.callback_query(F.data, AddEventState.adding_priority)
async def event_priority(callback: types.CallbackQuery, state: FSMContext):
    with Session() as session:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
            new_event.priority = Priority(callback.data)
            new_event.user_id = session.query(User).filter_by(telegram_user_id=callback.from_user.id).first().id
            session.add(new_event)
            session.commit()
            await state.clear()
            await callback.message.answer(text=config.success_text)
        except Exception as e:
            logging.error(e)


@router.callback_query(F.data, RepeatableEventState.adding_day)
async def every_day_event(state: FSMContext):
    try:
        await state.set_state(AddEventState.adding_remind_at)
    except Exception as e:
        logging.error(e)


@router.callback_query(F.data == RepeatDays.ALL_DAYS.value)
async def all_days_event(callback: CallbackQuery, state: FSMContext):
    new_event.repeat_type = RepeatType(callback)
    await callback.message.answer(text="Напишите время напоминания в формате '12:30' или '1230'")
    await push_state(state, AddEventState.adding_remind_at)


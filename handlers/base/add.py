import logging
from datetime import datetime, timedelta

from aiogram import types
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import sessionmaker
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot_state.state_stack import push_state
from const.callback.callback_types import InlineButtonType
from handlers.keyboard.inline import back, cancel_button
from handlers.time.time import set_time_remind, set_date_remind

from const.event.priority import Priority
from const.event.repeatable import RepeatType, RepeatDays, OnlyDay
from keyboards import keyboards
from aiogram import F
from handlers.filter.filter import IsPrivate

from bot_state.states import AddEventState, RepeatableEventState
from config import BotConfig
from db import engine, User
from keyboards.keyboards import get_cancel_return_keyboard


config = BotConfig()
router = Router()
Session = sessionmaker(bind=engine)

"""
    Для реализации возможности диалога с ботом и сохранением его состояния был использован 
    принцип Конечного Автомата с применением FSMContext
    Инициализация начального состояния происходит путем ввода команды – /add
    Сброс состояния бота – /cancel
"""

""" Обработчик команды /add """
@router.message(Command("add"), IsPrivate())
async def add_command(message: Message, state: FSMContext):
    try:
        await state.clear()
        await push_state(state, AddEventState.adding_title)
        await message.answer(
            text="Введите название события", parse_mode=ParseMode.HTML, reply_markup=keyboards.get_cancel_keyboard()
        )
    except Exception as e:
        logging.error(e)


""" Обработчик сообщения – Название ивента"""
@router.message(AddEventState.adding_title, F.text)
async def set_new_event_title(message: Message, state: FSMContext):
    try:
        await push_state(state, AddEventState.adding_description)
        await state.update_data(title=message.text)
        await message.answer(
            text="Введите описание события", reply_markup=get_cancel_return_keyboard()
        )
    except Exception as e:
        logging.error(e)


""" Обработчик сообщения – Описание ивента"""
@router.message(F.text, AddEventState.adding_description)
async def set_new_event_description(message: Message, state: FSMContext):
    try:
        await push_state(state, AddEventState.adding_status)
        await state.update_data(description=message.text)
        await message.answer(
            text="Выберите статус события", reply_markup=keyboards.get_status_keyboard()
        )
    except Exception as e:
        logging.error(e)


""" Обработчик Callback вызова – Статус ивента"""
@router.callback_query(F.data, AddEventState.adding_status)
async def set_new_event_status(callback: types.CallbackQuery, state: FSMContext):
    try:
        if callback.data == InlineButtonType.CANCEL.value:
            await cancel_button(callback, state)
            return
        if callback.data == InlineButtonType.RETURN.value:
            await back(callback, state)
            return

        await push_state(state, AddEventState.adding_repeatable)
        await state.update_data(status=callback.data)
        await callback.message.edit_text(
            text="Когда напомнить про событие",
            reply_markup=keyboards.get_repeatable_type_keyboard()
        )
    except Exception as e:
        logging.error(f"Ошибка в event_status: {e}")


""" Обработчик Callback вызова – Когда напоминать про событие"""
@router.callback_query(
    F.data.in_([r.value for r in RepeatType] + [InlineButtonType.CANCEL.value, InlineButtonType.RETURN.value]),
    AddEventState.adding_repeatable
)
async def set_new_event_repeatable(callback: types.CallbackQuery, state: FSMContext):
    try:
        match callback.data:
            case InlineButtonType.CANCEL.value:
                await cancel_button(callback, state)
                return
            case InlineButtonType.RETURN.value:
                await back(callback, state)
                return

        match callback.data:
            case RepeatType.ONLY_DAY.value:
                await state.update_data(repeatable=False)
                await state.update_data(repeat_type=RepeatType(callback.data))
                await push_state(state, AddEventState.adding_remind_date)
                await callback.message.edit_reply_markup(reply_markup=None)
                await callback.message.edit_text("Запишите дату и время, когда нужно напомнить в формате"
                                                 "\n«Месяц.День.Год Часы:Минуты»\nПример: «14.08.2025 09:00»",
                                                 reply_markup=keyboards.get_day_options_keyboard())
                return
            case RepeatType.EVERY_DAY.value:
                await state.update_data(repeatable=True)
                await state.update_data(repeat_type=RepeatType(callback.data))
                await push_state(state, RepeatableEventState.adding_day)

                await callback.message.edit_reply_markup(reply_markup=None)
                await callback.message.edit_text(
                    text="Выберите дни для повторения:",
                    reply_markup=keyboards.get_days_of_week_keyboard(selected_days=[])
                )
                return
    except Exception as e:
        logging.error(f"Ошибка в event_repeatable: {e}")


""" Обработчик Callback вызова – Выбор дней для напоминания"""
@router.callback_query(
    F.data.in_([d.value for d in RepeatDays] + [InlineButtonType.RETURN.value]),
    RepeatableEventState.adding_day
)
async def set_new_event_days_of_week(callback: CallbackQuery, state: FSMContext):
    try:
        if callback.data == InlineButtonType.RETURN.value:
            await back(callback, state)
            return
        day = callback.data
        data = await state.get_data()
        selected_days = data.get("selected_days", [])

        if day in selected_days:
            selected_days.remove(day)
        else:
            selected_days.append(day)

        await state.update_data(selected_days=selected_days)

        new_markup = keyboards.get_days_of_week_keyboard(selected_days=selected_days)

        await callback.message.edit_text(text="Выберите дни для повторения:", reply_markup=new_markup)
    except Exception as e:
        logging.error(e)


""" Обработчик Callback вызова – Подтверждение выбора дней"""
@router.callback_query(F.data == InlineButtonType.CONFIRM.value)
async def confirm_days(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        selected_days = data.get("selected_days", [])
        if not selected_days:
            await callback.message.answer(text="Нужно выбрать хотя бы один день")
            return
        await state.update_data(selected_days=selected_days)
        await push_state(state, AddEventState.adding_remind_at)
        await callback.message.edit_text("Напишите время напоминания в формате\n«12:30, 09:00» или «1230, 0900»",
                                         reply_markup=keyboards.get_cancel_return_keyboard())
    except Exception as e:
        logging.error(e)


""" Обработчик сообщения – Время напоминания 'HH:MM' """
@router.message(F.text, AddEventState.adding_remind_at)
async def set_new_event_remind_at(message: Message, state: FSMContext):
    try:
        now = datetime.now()
        remind_time = await set_time_remind(message)
        if remind_time is None:
            return
        if remind_time < now:
            remind_time += timedelta(days=1)

        await state.update_data(remind_at=remind_time)
        await message.answer(text="Приоритет события",
                             reply_markup=keyboards.get_priority_keyboard())
        await push_state(state, AddEventState.adding_priority)
    except Exception as e:
        logging.error(e)


""" Обработчик Callback вызова – Выбор приоритета"""
@router.callback_query(
    F.data.in_([p.value for p in Priority]),
    AddEventState.adding_priority
)
async def set_new_event_priority(callback: types.CallbackQuery, state: FSMContext):
    with Session() as session:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
            await state.update_data(priority=Priority(callback.data))
            await state.update_data(
                user_id=session.query(User).filter_by(telegram_user_id=callback.from_user.id).first().id)

            await callback.message.edit_text(text="Куда напомнить о событии?",
                                             reply_markup=keyboards.get_chat_type_keyboard())
            await push_state(state, AddEventState.adding_privacy)
        except Exception as e:
            logging.error(e)


""" Обработчик сообщения – Сегодняшняя дата напоминания  """
@router.callback_query(F.data == OnlyDay.TODAY.value)
async def set_event_day_today(callback: CallbackQuery, state: FSMContext):
    await push_state(state, AddEventState.adding_remind_at)
    await callback.message.edit_text("Напишите время напоминания в формате\n«12:30, 09:00» или «1230, 0900»",
                                     reply_markup=keyboards.get_cancel_return_keyboard())


""" Обработчик сообщения – Определенная дата напоминания 'mm.dd.year HH:MM' """
@router.message(F.text, AddEventState.adding_remind_date)
async def set_new_event_remind_date(message: Message, state: FSMContext):
    try:
        remind_time = await set_date_remind(message)
        if remind_time is None:
            return
        await state.update_data(remind_at=remind_time)
        await message.answer(text="Приоритет события",
                             reply_markup=keyboards.get_priority_keyboard())
        await push_state(state, AddEventState.adding_priority)
    except Exception as e:
        logging.error(e)
import logging
from datetime import datetime, timedelta

from aiogram import types
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import sessionmaker
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from const.callback.callback_types import InlineButtonType
from const.event.chat import Chat
from handlers.keyboard.inline import back, cancel_button
from handlers.reminders.time import set_time_remind

from const.event.status import Status
from const.event.priority import Priority
from const.event.repeatable import RepeatType, RepeatDays
from keyboards import keyboards
from aiogram import F
from handlers.filter.filter import IsPrivate

from bot_state.states import AddEventState, RepeatableEventState
from config import BotConfig
from db import Event, engine, User, Group
from keyboards.keyboards import cancel_back_button

config = BotConfig()
router = Router()
Session = sessionmaker(bind=engine)

"""
    Для реализации возможности диалога с ботом и сохранением его состояния был использован 
    принцип Конечного Автомата с применением FSMContext
    Инициализация начального состояния происходит путем ввода команды – /add
    Сброс состояния бота – /cancel
"""


async def push_state(state: FSMContext, new_state):
    logging.info("Calling push_state")
    data = await state.get_data()
    history = data.get("history", [])
    current_state = await state.get_state()
    logging.info(f"Current state: {current_state}")
    if current_state:
        history.append(current_state)
    await state.update_data(history=history)
    await state.set_state(new_state)


""" Обработчик команды /add """


@router.message(StateFilter(None), Command("add"), IsPrivate())
async def cmd_add(message: Message, state: FSMContext):
    try:
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
        await state.update_data(title=message.text)
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
        await state.update_data(description=message.text)
        await message.answer(
            text="Выберите статус события", reply_markup=keyboards.status_inline_kb()
        )
    except Exception as e:
        logging.error(e)


""" Обработчик Callback вызова – Статус ивента"""


@router.callback_query(F.data, AddEventState.adding_status)
async def event_status(callback: types.CallbackQuery, state: FSMContext):
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
            reply_markup=keyboards.repeatable_inline_kb()
        )
    except Exception as e:
        logging.error(f"Ошибка в event_status: {e}")


""" Обработчик Callback вызова – Когда напоминать про событие"""


@router.callback_query(
    F.data.in_([r.value for r in RepeatType] + [InlineButtonType.CANCEL.value, InlineButtonType.RETURN.value]),
    AddEventState.adding_repeatable
)
async def event_repeatable(callback: types.CallbackQuery, state: FSMContext):
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
                await push_state(state, AddEventState.adding_remind_at)
                await callback.message.edit_reply_markup(reply_markup=None)
                await callback.message.edit_text("Напишите время напоминания в формате '12:30' или '1230'",
                                                 reply_markup=keyboards.cancel_back_button())
                return
            case RepeatType.EVERY_DAY.value:
                await state.update_data(repeatable=True)
                await state.update_data(repeat_type=RepeatType(callback.data))
                await push_state(state, RepeatableEventState.adding_day)

                await callback.message.edit_reply_markup(reply_markup=None)
                await callback.message.edit_text(
                    text="Выберите дни для повторения:",
                    reply_markup=keyboards.days_of_week_inline_kb(selected_days=[])
                )
                return


    except Exception as e:
        logging.error(f"Ошибка в event_repeatable: {e}")


@router.callback_query(
    F.data.in_([d.value for d in RepeatDays]),
    RepeatableEventState.adding_day
)
async def select_repeat_day(callback: CallbackQuery, state: FSMContext):
    day = callback.data
    data = await state.get_data()
    selected_days = data.get("selected_days", [])

    if day in selected_days:
        selected_days.remove(day)
    else:
        selected_days.append(day)

    await state.update_data(selected_days=selected_days)

    new_markup = keyboards.days_of_week_inline_kb(selected_days=selected_days)

    await callback.message.edit_text(text="Выберите дни для повторения:", reply_markup=new_markup)


""" Обработчик сообщения – Время напоминания 'HH:MM' """


@router.message(F.text, AddEventState.adding_remind_at)
async def event_remind_at(message: Message, state: FSMContext):
    try:
        now = datetime.now()
        remind_time = await set_time_remind(message)
        if remind_time is None:
            return
        if remind_time < now:
            remind_time += timedelta(days=1)

        await state.update_data(remind_at=remind_time)
        await message.answer(text="Приоритет события",
                             reply_markup=keyboards.priority_inline_kb())
        await push_state(state, AddEventState.adding_priority)
    except Exception as e:
        logging.error(e)


@router.callback_query(
    F.data.in_([p.value for p in Priority]),
    AddEventState.adding_priority
)
async def event_priority(callback: types.CallbackQuery, state: FSMContext):
    with Session() as session:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
            await state.update_data(priority=Priority(callback.data))
            await state.update_data(
                user_id=session.query(User).filter_by(telegram_user_id=callback.from_user.id).first().id)

            await callback.message.edit_text(text="Куда напомнить о событии?",
                                             reply_markup=keyboards.chat_type_inline_kb())
            await push_state(state, AddEventState.adding_private)
        except Exception as e:
            logging.error(e)


@router.callback_query(F.data == Chat.GROUP.value)
async def event_group_id(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.edit_text(text="Введите ID группы", reply_markup=None)
        await push_state(state, AddEventState.adding_group)
    except Exception as e:
        logging.error(e)


@router.message(F.text, AddEventState.adding_group)
async def event_group(message: Message, state: FSMContext):
    with Session() as session:
        try:
            data = await state.get_data()
            user = session.query(User).filter_by(telegram_user_id=message.from_user.id).first()

            new_group = Group(
                telegram_group_id=int(message.text),
                user_id=user.id,
            )
            session.add(new_group)
            session.flush()

            new_event = Event(
                title=data.get("title"),
                description=data.get("description"),
                status=Status(data.get("status")),
                repeatable=data.get("repeatable"),
                repeat_type=RepeatType(data.get("repeat_type")),
                remind_at=data.get("remind_at"),
                remind_time=data.get("remind_at").time(),
                priority=Priority(data.get("priority")),
                chat_type=Chat.GROUP.value,
                telegram_chat_id=message.chat.id,
                group_id=new_group.id,
                user_id=user.id
            )

            session.add(new_event)
            session.commit()
            await state.clear()
            await message.answer(text=config.success_text)
        except Exception as e:
            logging.error(e)


@router.callback_query(F.data == Chat.PRIVATE.value)
async def event_private(callback: types.CallbackQuery, state: FSMContext):
    with Session() as session:
        try:
            data = await state.get_data()
            user = session.query(User).filter_by(telegram_user_id=callback.from_user.id).first()

            new_event = Event(
                title=data.get("title"),
                description=data.get("description"),
                status=Status(data.get("status")),
                repeatable=data.get("repeatable"),
                repeat_type=RepeatType(data.get("repeat_type")),
                remind_at=data.get("remind_at"),
                remind_time=data.get("remind_at").time(),
                priority=Priority(data.get("priority")),
                chat_type=Chat.PRIVATE.value,
                telegram_chat_id=callback.message.chat.id,
                user_id=user.id
            )

            session.add(new_event)
            session.commit()
            await state.clear()
            await callback.message.edit_text(text=config.success_text, reply_markup=None)

        except Exception as e:
            logging.error(e)


@router.callback_query(F.data == RepeatDays.ALL_DAYS.value)
async def all_days_event(callback: CallbackQuery, state: FSMContext):
    await state.update_data(repeat_type=RepeatType(callback))
    await callback.message.answer(text="Напишите время напоминания в формате '12:30' или '1230'")
    await push_state(state, AddEventState.adding_remind_at)

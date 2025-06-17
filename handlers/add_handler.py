import logging

from aiogram import types
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from keyboards import for_event_type
from aiogram import F

from bot_state.add_event_state import AddEventState
from config import BotConfig
from db import Event, engine, User

config = BotConfig()
router = Router()
Session = sessionmaker(bind=engine)
session = Session()
new_event = Event()


@router.message(StateFilter(None), Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    try:
        new_event.telegram_chat_id = message.chat.id
        await state.set_state(AddEventState.adding_title)
        await message.answer(
            text="Введите название события", parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logging.error(e)


@router.message(AddEventState.adding_title, F.text)
async def event_title(message: Message, state: FSMContext):
    try:
        await state.set_state(AddEventState.adding_description)
        new_event.title = message.text  # Сохраняем название события
        await message.answer(
            text="Введите описание события"
        )
    except Exception as e:
        logging.error(e)


@router.message(F.text, AddEventState.adding_description)
async def event_description(message: Message, state: FSMContext):
    try:
        await state.set_state(AddEventState.adding_status)
        new_event.description = message.text  # Сохраняем описание события
        await message.answer(
            text="Выберите статус события", reply_markup=for_event_type.status_inline_kb()
        )
    except Exception as e:
        logging.error(e)


@router.callback_query(F.data, AddEventState.adding_status)
async def event_status(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.set_state(AddEventState.adding_repeatable)
        new_event.status = callback.data.__str__()
        await callback.message.answer(text="Выберите когда повторять событие",
                                      reply_markup=for_event_type.repeatable_inline_kb())
    except Exception as e:
        logging.error(e)

@router.callback_query(F.data, AddEventState.adding_repeatable)
async def event_repeatable(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.set_state(AddEventState.adding_priority)
        new_event.repeat_type = callback.data.__str__()
        await callback.message.answer(text="Выберите приоритет события",
                                      reply_markup=for_event_type.priority_inline_kb())
    except Exception as e:
        logging.error(e)

@router.callback_query(F.data, AddEventState.adding_priority)
async def event_priority(callback: types.CallbackQuery, state: FSMContext):
    try:
        new_event.priority = callback.data.__str__()  # Сохраняем приоритет события
        new_event.user_id = session.query(User).filter_by(telegram_user_id=callback.from_user.id).first().id
        session.add(new_event)
        session.commit()
        await state.set_data({})
    except Exception as e:
        logging.error(e)

import logging

from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker

from bot_state.states import AddEventState
from const.event.chat import Chat
from const.event.priority import Priority
from aiogram import F

from handlers.base.add import push_state
from keyboards import keyboards

from config import BotConfig
from db import engine, Event, Group

config = BotConfig()
router = Router()
Session = sessionmaker(bind=engine)


@router.message(Command("list"))
async def list_command(message: Message, state: FSMContext):
    await state.clear()
    if message.chat.type == "private":
        await message.answer(text="Выбор ...", reply_markup=keyboards.get_private_events_filter_keyboard())
        await push_state(state, AddEventState.events_list)
    else:
        await message.answer(text="Выбор ...", reply_markup=keyboards.get_group_events_filter_keyboard())
        await push_state(state, AddEventState.events_list)


@router.callback_query(F.data == 'all')
async def get_all_events(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    print(callback.message.chat.id)

    try:
        with Session() as session:
            chat = callback.message.chat
            chat_id = chat.id


            groups = session.query(Group).filter_by(telegram_group_id=chat_id).all()

            if chat.type == "private":
                events = session.query(Event).filter_by(telegram_chat_id=chat_id).all()

                for event in events:
                    await callback.message.answer(text=str(event), parse_mode="HTML",
                                                  reply_markup=keyboards.get_event_action_keyboard(event.id))

                if not events:
                    await callback.message.edit_text("Нет событий.")
                    await state.clear()
                    return
            else:
                if not groups:
                    await callback.message.edit_text("Группа отсутствует.")
                    await state.clear()
                    return

                events = []
                for group in groups:
                    group_events = session.query(Event).filter_by(group_id=group.id).all()
                    events.extend(group_events)

                if not events:
                    await callback.message.edit_text("Нет событий.")
                    await state.clear()
                    return

                for event in events:
                    await callback.message.answer(text=str(event), parse_mode="HTML")
            await state.clear()

    except Exception as e:
        logging.error(e)


@router.callback_query(F.data.in_(['group', 'private']))
async def group_events_list(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
        with Session() as session:
            events = session.query(Event).filter_by(chat_type=Chat.GROUP.value).all()
            match callback.data:
                case "group":

                    if not events:
                        await callback.message.edit_text(text="Нет событий.")
                    for event in events:
                        await callback.message.answer(text=str(event),
                                                      reply_markup=keyboards.get_event_action_keyboard(event.id))
                    await state.clear()
                    return
                case "private":
                    if not events:
                        await callback.message.edit_text(text="Нет событий.")
                    for event in events:
                        await callback.message.answer(text=str(event),
                                                      reply_markup=keyboards.get_event_action_keyboard(event.id))
                    await state.clear()
                    return
    except Exception as e:
        logging.error(e)


@router.callback_query(F.data == 'priority', AddEventState.events_list)
async def priority_list_handler(callback: types.CallbackQuery, state: FSMContext):
    await push_state(state, AddEventState.events_priority)
    await callback.message.edit_text(text="По какому критерию", reply_markup=keyboards.get_priority_keyboard())


@router.callback_query(lambda c: c.data in [p.value for p in Priority])
async def priority_list_status_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    try:
        with (Session() as session):
            priority_value = Priority(callback.data)
            chat_id = callback.message.chat.id

            if callback.message.chat.type == "private":
                events = session.query(Event).filter(
                    Event.telegram_chat_id == chat_id,
                    Event.priority == priority_value
                ).all()

            else:
                groups = session.query(Group).filter_by(telegram_group_id=chat_id).all()
                if not groups:
                    await callback.message.edit_text("В группе нет событий.")

                events = []
                for group in groups:
                    group_events = session.query(Event).filter(
                        Event.group_id == group.id,
                        Event.priority == priority_value
                    ).all()
                    events.extend(group_events)

            if not events:
                await callback.message.edit_text("Нет событий с таким приоритетом.")

            for event in events:
                await callback.message.answer(text=str(event), parse_mode="HTML")
            await state.clear()
    except Exception as e:
        logging.error(e)

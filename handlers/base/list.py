import logging

from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker

from bot_state.states import AddEventState, EventsListFilter
from const.event.chat import Chat
from const.event.priority import Priority
from aiogram import F

from const.event.status import Status
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
        await message.answer(text="📋 <b>Выберите, какие события вы хотите увидеть:</b>",
                             reply_markup=keyboards.get_private_events_filter_keyboard())
        await push_state(state, EventsListFilter.events_list)
    else:
        await message.answer(text="📋 <b>Выберите, какие события вы хотите увидеть:</b>",
                             reply_markup=keyboards.get_group_events_filter_keyboard())
        await push_state(state, EventsListFilter.events_list)


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
                    await callback.message.edit_text("<b>Нет событий</b>.")
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
                    await callback.message.edit_text("<b>Нет событий</b>.")
                    await state.clear()
                    return

                for event in events:
                    await callback.message.answer(text=str(event), parse_mode="HTML")
            await state.clear()

    except Exception as e:
        logging.error(e)
        await state.clear()


@router.callback_query(F.data.in_(['group', 'private']))
async def group_events_list(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
        with Session() as session:
            match callback.data:
                case "group":
                    events = session.query(Event).filter_by(chat_type=Chat.GROUP.value).all()
                    if not events:
                        await callback.message.edit_text(text="<b>Нет событий</b>.")
                    for event in events:
                        await callback.message.answer(text=str(event),
                                                      reply_markup=keyboards.get_event_action_keyboard(event.id))
                    await state.clear()
                    return
                case "private":
                    events = session.query(Event).filter_by(chat_type=Chat.PRIVATE.value).all()
                    if not events:
                        await callback.message.edit_text(text="<b>Нет событий</b>.")
                    for event in events:
                        await callback.message.answer(text=str(event),
                                                      reply_markup=keyboards.get_event_action_keyboard(event.id))
                    await state.clear()
                    return
    except Exception as e:
        logging.error(e)
        await state.clear()


@router.callback_query(F.data == 'priority', EventsListFilter.events_list)
async def priority_list_handler(callback: types.CallbackQuery, state: FSMContext):
    await push_state(state, EventsListFilter.events_priority_filter)
    await callback.message.edit_text(text="По какому критерию", reply_markup=keyboards.get_priority_keyboard())


@router.callback_query(F.data == 'status', EventsListFilter.events_list)
async def priority_list_handler(callback: types.CallbackQuery, state: FSMContext):
    await push_state(state, EventsListFilter.events_status_filter)
    await callback.message.edit_text(text="По какому статусу", reply_markup=keyboards.get_status_keyboard())


@router.callback_query(lambda c: c.data in [p.value for p in Priority], EventsListFilter.events_priority_filter)
async def priority_list_filter(callback: types.CallbackQuery, state: FSMContext):
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
                for event in events:
                    await callback.message.answer(text=str(event), parse_mode="HTML",
                                                  reply_markup=keyboards.get_event_action_keyboard(event.id))

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
                    for event in events:
                        await callback.message.answer(text=str(event), parse_mode="HTML")

            if not events:
                await callback.message.edit_text("Нет событий с таким приоритетом.")
            await state.clear()
    except Exception as e:
        logging.error(e)
        await state.clear()


@router.callback_query(lambda c: c.data in [p.value for p in Status], EventsListFilter.events_status_filter)
async def status_list_filter(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    try:
        with (Session() as session):
            status_value = Status(callback.data)
            chat_id = callback.message.chat.id

            if callback.message.chat.type == "private":
                events = session.query(Event).filter(
                    Event.telegram_chat_id == chat_id,
                    Event.status == status_value
                ).all()
                for event in events:
                    await callback.message.answer(text=str(event), parse_mode="HTML",
                                                  reply_markup=keyboards.get_event_action_keyboard(event.id))

            else:
                groups = session.query(Group).filter_by(telegram_group_id=chat_id).all()
                if not groups:
                    await callback.message.edit_text("В группе нет событий.")

                events = []
                for group in groups:
                    group_events = session.query(Event).filter(
                        Event.group_id == group.id,
                        Event.status == status_value
                    ).all()
                    events.extend(group_events)
                    for event in events:
                        await callback.message.answer(text=str(event), parse_mode="HTML")

            if not events:
                await callback.message.edit_text("Нет событий с таким статусом.")
            await state.clear()
    except Exception as e:
        logging.error(e)
        await state.clear()

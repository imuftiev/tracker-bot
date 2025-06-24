from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker
from const.event.priority import Priority
from aiogram import F

from keyboards import keyboards

from config import BotConfig
from db import engine, Event, Group

config = BotConfig()
router = Router()
Session = sessionmaker(bind=engine)


@router.message(StateFilter(None), Command("list"))
async def event_list_handler(message: Message):
    await message.answer(text="Выбор ...", reply_markup=keyboards.events_list_inline_kb())


@router.callback_query(F.data == 'all')
async def todo_status_events_list(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    print(callback.message.chat.id)

    with Session() as session:
        chat = callback.message.chat
        chat_id = chat.id

        groups = session.query(Group).filter_by(telegram_group_id=chat_id).all()

        if chat.type == "private":
            events = session.query(Event).filter_by(telegram_chat_id=chat_id).all()
        else:
            if not groups:
                await callback.message.answer("В группе нет событий.")
                return

            events = []
            for group in groups:
                group_events = session.query(Event).filter_by(group_id=group.id).all()
                events.extend(group_events)

        if not events:
            await callback.message.answer("Нет событий.")
            return

        for event in events:
            await callback.message.answer(
                text=str(event),
                parse_mode="HTML"
            )


@router.callback_query(F.data == 'priority')
async def priority_list_handler(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text="По какому критерию", reply_markup=keyboards.priority_inline_kb())


@router.callback_query(lambda c: c.data in [p.value for p in Priority])
async def priority_list_status_handler(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)

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
                await callback.message.answer("В группе нет событий.")
                return

            events = []
            for group in groups:
                group_events = session.query(Event).filter(
                    Event.group_id == group.id,
                    Event.priority == priority_value
                ).all()
                events.extend(group_events)

        if not events:
            await callback.message.answer("Нет событий с таким приоритетом.")
            return

        for event in events:
            await callback.message.answer(text=str(event), parse_mode="HTML")

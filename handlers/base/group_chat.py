import logging

from aiogram import Router, types
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker

from bot_state.states import AddEventState
from config import BotConfig
from const.event.chat import Chat
from const.event.priority import Priority
from const.event.repeatable import RepeatType
from const.event.status import Status
from db import engine, User, Event, Group
from handlers.base.add import push_state
from scheduler.apscheduler import schedule_repeatable_event

Session = sessionmaker(bind=engine)
router = Router()
config = BotConfig()

@router.callback_query(F.data == Chat.GROUP.value)
async def set_new_event_group_id(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.edit_text(text="Введите ID группы", reply_markup=None)
        await push_state(state, AddEventState.adding_group)
    except Exception as e:
        logging.error(e)


"""
    Обработчик инлайн-кнопки. Добавление события в групповой чат.
"""
@router.message(F.text, AddEventState.adding_group)
async def set_new_event_group(message: Message, state: FSMContext):
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
                days_of_week=data.get("selected_days"),
                priority=Priority(data.get("priority")),
                chat_type=Chat.GROUP.value,
                telegram_chat_id=message.chat.id,
                group_id=new_group.id,
                user_id=user.id
            )
            session.add(new_event)
            session.commit()
            session.refresh(new_event)
            schedule_repeatable_event(new_event)
            await state.clear()
            await message.answer(text=config.success_text)
        except Exception as e:
            logging.error(e)
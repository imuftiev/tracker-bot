import logging

from aiogram import Router, types
from aiogram import F
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker

from config import BotConfig
from const.event.chat import Chat
from const.event.priority import Priority
from const.event.repeatable import RepeatType
from const.event.status import Status
from db import engine, User, Event
from scheduler.apscheduler import schedule_repeatable_event, schedule_one_time_event

Session = sessionmaker(bind=engine)
router = Router()
config = BotConfig()

"""
    Обработчик инлайн-кнопки. Добавление события в личный чат.
"""


@router.callback_query(F.data == Chat.PRIVATE.value)
async def set_new_event_private(callback: types.CallbackQuery, state: FSMContext):
    with Session() as session:
        try:
            data = await state.get_data()
            user = session.query(User).filter_by(telegram_user_id=callback.from_user.id).first()
            if not user:
                user = User(telegram_user_id=callback.from_user.id, username=callback.from_user.username)
                session.add(user)
                session.commit()
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
                month=data.get("selected_months"),
                days_of_week=data.get("selected_days"),
                days_of_month=data.get("selected_month_days"),
                telegram_chat_id=callback.message.chat.id,
                user_id=user.id
            )

            session.add(new_event)
            session.commit()
            session.refresh(new_event)
            if not new_event.repeatable:
                schedule_one_time_event(new_event)
            else:
                schedule_repeatable_event(new_event)
            await state.clear()
            await callback.message.edit_text(text=config.success_text, reply_markup=None)

        except Exception as e:
            logging.error(e)

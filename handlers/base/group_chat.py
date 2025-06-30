import logging

from aiogram import Router, types
from aiogram import F
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker

from bot_state.states import AddEventState
from config import BotConfig
from const.event.chat import Chat
from const.event.priority import Priority
from const.event.repeatable import RepeatType
from const.event.status import Status
from db import engine, User, Event, Group
from handlers.base.add import push_state
from scheduler.apscheduler import schedule_repeatable_event, schedule_one_time_event
from keyboards import keyboards

Session = sessionmaker(bind=engine)
router = Router()
config = BotConfig()


@router.callback_query(F.data == Chat.GROUP.value)
async def set_new_event_group_id(callback: types.CallbackQuery, state: FSMContext):
    try:
        await push_state(state, AddEventState.adding_group)
        with Session() as session:
            groups = session.query(Group).all()
            if not groups:
                await callback.message.edit_text(text="❌ <b>Вы не прикрепили ни одной группы</b>")
                await callback.message.answer(text="📍 <b>Куда напомнить о событии?</b>",
                                              reply_markup=keyboards.get_chat_type_keyboard())
                await push_state(state, AddEventState.adding_privacy)
                return
            await callback.message.edit_text(text="✳️ <b>Выберите группу</b>",
                                             reply_markup=keyboards.get_groups_keyboard(callback))
    except Exception as e:
        logging.error(e)


"""
    Обработчик инлайн-кнопки. Добавление события в групповой чат.
"""


@router.callback_query(F.data, AddEventState.adding_group)
async def set_new_event_group(callback: types.CallbackQuery, state: FSMContext):
    with Session() as session:
        try:
            data = await state.get_data()
            logging.info(f"Получен callback group_id: {callback.data}")

            telegram_group_id = int(callback.data)

            user = session.query(User).filter_by(telegram_user_id=callback.from_user.id).first()
            if not user:
                user = User(telegram_user_id=callback.from_user.id, username=callback.from_user.username)
                session.add(user)
                session.commit()
            group = session.query(Group).filter_by(telegram_group_id=telegram_group_id).first()
            logging.info(f"GROUP:{group.id}")

            new_event = Event(
                title=data.get("title"),
                description=data.get("description"),
                status=Status(data.get("status")),
                repeatable=data.get("repeatable"),
                repeat_type=RepeatType(data.get("repeat_type")),
                remind_at=data.get("remind_at"),
                remind_time=data.get("remind_at").time(),
                days_of_week=data.get("selected_days"),
                days_of_month=data.get("selected_month_days"),
                priority=Priority(data.get("priority")),
                chat_type=Chat.GROUP.value,
                telegram_chat_id=callback.message.chat.id,
                group_id=group.id,
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
            await callback.message.answer(text=config.success_text)
        except Exception as e:
            logging.error(e)

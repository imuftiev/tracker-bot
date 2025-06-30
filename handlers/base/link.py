import logging

from aiogram.filters import Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker

from bot_state.state_stack import push_state
from bot_state.states import LinkGroupState
from db import engine, Group, User
from handlers.filter.filter import IsPrivate

router = Router()
Session = sessionmaker(bind=engine)


@router.message(Command("link"), IsPrivate())
async def link_command(message: Message, state: FSMContext):
    try:
        await state.clear()
        await message.answer("🆕 Введите <b>название</b> группы")
        await push_state(state, LinkGroupState.attach_chat_name)
    except Exception as e:
        logging.error(e)
        await state.clear()


@router.message(F.text, LinkGroupState.attach_chat_name)
async def set_group_chat_name(message: Message, state: FSMContext):
    try:
        await state.update_data(group_chat_name=message.text)
        await push_state(state, LinkGroupState.attach_id)
        await message.answer("🆔 Введите <b>ID</b> группы")
    except Exception as e:
        logging.error(e)
        await state.clear()
        await message.answer("Ошибка, попробуйте снова")


@router.message(F.text, LinkGroupState.attach_id)
async def set_group_chat_id(message: Message, state: FSMContext):
    try:
        group_chat_id = message.text.replace(" ", "")
        await state.update_data(group_chat_id=group_chat_id)
        data = await state.get_data()
        with Session() as session:
            user = session.query(User).filter_by(telegram_user_id=message.from_user.id).first()
            group = Group(
                name=data.get("group_chat_name"),
                telegram_group_id=data.get("group_chat_id"),
                user_id=user.id,
            )
            session.add(group)
            session.commit()
            session.flush()
            await state.clear()
        await message.answer("✅ Группа <b>успешно</b> привязана")
    except Exception as e:
        logging.error(e)
        await message.answer("Ошибка, попробуйте снова")
        await state.clear()

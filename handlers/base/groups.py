import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker

from db import engine, Group
from handlers.filter.filter import IsPrivate
from keyboards import keyboards

router = Router()
Session = sessionmaker(bind=engine)


@router.message(Command("groups"), IsPrivate())
async def groups_command(message: Message):
    try:
        with Session() as session:
            groups = session.query(Group).all()
            if not groups:
                await message.answer(text="❌ Группы <b>не найдены</b>")
            await message.answer("👥 <b>Прикрепленные</b> группы")
            for group in groups:
                await message.answer(text=f"👨‍👩‍👦‍👦 {str(group.name)}",
                                     reply_markup=keyboards.get_group_action_keyboard(int(group.id)))
    except Exception as e:
        logging.error(e)

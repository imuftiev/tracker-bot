from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker

from bot_state.states import GroupLinkState
from db import Group, engine
from keyboards import keyboards

router = Router()
group = Group()
Session = sessionmaker(bind=engine)


@router.message(StateFilter(None), Command("link"))
async def link_cmd(message: Message, state: FSMContext):
    await message.answer(text="В какую группу присылать уведомления?\nID:", reply_markup=keyboards.cancel_button())
    await state.set_state(GroupLinkState.attach_link)

@router.message(F.text, GroupLinkState.attach_link)
async def attach_link_cmd(message: Message, state: FSMContext):
    with Session() as session:

        group.telegram_group_id = message.text
        session.add(group)
        session.commit()
        await state.clear()

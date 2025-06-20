from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker
from aiogram import F

from keyboards import keyboards

from config import BotConfig
from db import engine, Event

config = BotConfig()
router = Router()
Session = sessionmaker(bind=engine)


@router.message(StateFilter(None), Command("list"))
async def event_list_handler(message: Message):
    await message.answer(text= "Вывод", reply_markup=keyboards.events_list_inline_kb())


@router.callback_query(F.data == 'all')
async def todo_status_events_list(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    with Session() as session:
        event_list = session.query(Event).filter_by(telegram_chat_id=callback.from_user.id).all()
        for event in event_list:
            await callback.message.answer(
                text=(
                    f"🆔<i>\t{event.id}</i>\n"
                    f"🔔<i>\t{event.title}</i>\n"
                    f"📝<i>\t{event.description or '—'}</i>\n"
                    f"❓<i>\t{event.status.value}</i>\n"
                    f"✔️<i>\t{event.priority.value}</i>\n"
                )
            )


@router.callback_query(F.data == 'priority')
async def priority_list_handler(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text="По какому критерию", reply_markup=keyboards.priority_inline_kb())

from const.event.priority import Priority

@router.callback_query(lambda c: c.data in [p.value for p in Priority])
async def priority_list_status_handler(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    with Session() as session:
        priority_value = Priority(callback.data)

        event_list = session.query(Event).filter(
            Event.telegram_chat_id == callback.from_user.id,
            Event.priority == priority_value
        ).all()

    if not event_list:
        await callback.message.answer("Нет событий с таким приоритетом.")
        return

    for event in event_list:
        await callback.message.answer(
            text=(
                f"🆔<i>\t{event.id}</i>\n"
                f"🔔<i>\t{event.title}</i>\n"
                f"📝<i>\t{event.description or '—'}</i>\n"
                f"❓\t{event.status.value}\n"
                f"✔️\t{event.priority.value}\n"
            ),
            parse_mode="HTML"
        )

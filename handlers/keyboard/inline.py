from aiogram import Router
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.orm import Session

from bot_state.states import AddEventState
from config import BotConfig
from const.callback.callback_types import InlineButtonType
from keyboards import keyboards

router = Router()
config = BotConfig()


@router.callback_query(F.data == InlineButtonType.CANCEL.value)
async def cancel_button(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    with Session() as session:
        if data is not None:
            await state.clear()
        session.flush()
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(text=config.cancel_text)


@router.callback_query(F.data == InlineButtonType.RETURN.value)
async def back(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    history = data.get("history", []) if data else []
    if not history:
        await callback.answer("Нельзя вернуться назад.")
        return

    previous_state = history.pop()
    await state.update_data(history=history)
    await state.set_state(previous_state)

    if previous_state == AddEventState.adding_title:
        await callback.message.edit_text("Введите название события")
    elif previous_state == AddEventState.adding_description:
        await callback.message.edit_text("Введите описание события")
    elif previous_state == AddEventState.adding_status:
        await callback.message.edit_text(
            "Выберите статус события", reply_markup=keyboards.status_inline_kb())
    elif previous_state == AddEventState.adding_repeatable:
        await callback.message.edit_text(
            "Когда напомнить про событие", reply_markup=keyboards.repeatable_inline_kb())

    await callback.answer()

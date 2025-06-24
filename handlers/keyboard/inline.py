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

    match previous_state:
        case AddEventState.adding_title:
            await callback.message.edit_text(text="Введите название события",reply_markup=keyboards.cancel_button())
            return
        case AddEventState.adding_description:
            await callback.message.edit_text("Введите описание события", reply_markup=keyboards.cancel_back_button())
            return
        case AddEventState.adding_status:
            await callback.message.edit_text("Выберите статус события", reply_markup=keyboards.status_inline_kb())
            return
        case AddEventState.adding_repeatable:
            await callback.message.edit_text(
                "Когда напомнить про событие", reply_markup=keyboards.repeatable_inline_kb())
            return
        case AddEventState.adding_remind_at:
            await callback.message.edit_text("Напишите время напоминания в формате '12:30' или '1230'",
                                          reply_markup=keyboards.cancel_back_button())
            return
        case AddEventState.adding_priority:
            await callback.message.edit_text(
                "Приоритет события", reply_markup=keyboards.priority_inline_kb())
            return
    await callback.answer()

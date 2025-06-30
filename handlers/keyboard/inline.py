from aiogram import Router
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.orm import Session

from bot_state.states import AddEventState, RepeatableEventState, UpdateEventState, EventsListFilter
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
        await callback.message.edit_text(text=config.cancel_text, reply_markup=None)


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
        case EventsListFilter.events_list:
            if callback.message.chat.type == "private":
                await callback.message.edit_text(text="Выбор ...",
                                                 reply_markup=keyboards.get_private_events_filter_keyboard())
            else:
                await callback.message.edit_text(text="Выбор ...",
                                                 reply_markup=keyboards.get_group_events_filter_keyboard())
            return
        case AddEventState.adding_title:
            await callback.message.edit_text(text="Введите название события",
                                             reply_markup=keyboards.get_cancel_keyboard())
            return
        case AddEventState.adding_description:
            await callback.message.edit_text("Введите описание события",
                                             reply_markup=keyboards.get_cancel_return_keyboard())
            return
        case AddEventState.adding_status:
            await callback.message.edit_text("Выберите статус события", reply_markup=keyboards.get_status_keyboard())
            return
        case AddEventState.adding_remind_date:
            await callback.message.edit_text("Запишите дату и время, когда нужно напомнить в формате"
                                             "\n«Месяц.День.Год Часы:Минуты»\nПример: «14.08.2025 09:00»",
                                             reply_markup=keyboards.get_day_options_keyboard())
            return
        case AddEventState.adding_repeatable:
            await callback.message.edit_text(
                "Когда напомнить про событие", reply_markup=keyboards.get_repeatable_type_keyboard())
            return
        case RepeatableEventState.adding_days:
            data = await state.get_data()
            selected_days = data.get("selected_days", [])
            await callback.message.edit_text(
                text="Выберите дни для повторения:",
                reply_markup=keyboards.get_days_of_week_keyboard(selected_days=selected_days)
            )
            return
        case AddEventState.adding_remind_at:
            await callback.message.edit_text("Напишите время напоминания в формате\n«12:30, 09:00» или «1230, 0900»",
                                             reply_markup=keyboards.get_cancel_return_keyboard())
            return
        case AddEventState.adding_privacy:
            await callback.message.edit_text(text="📍 <b>Куда напомнить о событии?</b>",
                                             reply_markup=keyboards.get_chat_type_keyboard())
            return
        case AddEventState.adding_priority:
            await callback.message.edit_text(
                "Приоритет события", reply_markup=keyboards.get_priority_keyboard())
            return
        case UpdateEventState.updating:
            event_id = data.get("event_id")
            await callback.message.edit_text(
                text="Что изменить в событии",
                reply_markup=keyboards.update_event_keyboard(event_id)
            )
            return
    await callback.answer()

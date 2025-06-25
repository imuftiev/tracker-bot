from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

import config
from const.event.chat import Chat
from const.callback.delete import DeleteEvent
from const.event.status import Status
from const.event.priority import Priority
from const.event.repeatable import RepeatType, RepeatDays
from const.callback.callback_types import InlineButtonType
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from const.event.repeatable import RepeatDays

config = config.BotConfig()


def days_of_week_inline_kb(selected_days: list[str] = None) -> InlineKeyboardMarkup:
    selected_days = selected_days or []
    buttons = []

    for day in RepeatDays:
        is_selected = day.value in selected_days
        text = f"🔸{day.value}" if is_selected else day.value
        buttons.append([InlineKeyboardButton(
            text=text,
            callback_data=day.value
        )])

    buttons.append([
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=InlineButtonType.CONFIRM.value),
        InlineKeyboardButton(text="⬅️ Назад", callback_data=InlineButtonType.RETURN.value),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def cancel_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value))
    return builder.as_markup(resize_keyboard=True)


def cancel_back_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=config.back_text, callback_data=InlineButtonType.RETURN.value))
    builder.row(types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value))
    return builder.as_markup(resize_keyboard=True)


def repeatable_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    inline_keyboard = [
        types.InlineKeyboardButton(text="Каждый день", callback_data=RepeatType.EVERY_DAY.value),
        types.InlineKeyboardButton(text="Каждую неделю", callback_data=RepeatType.EVERY_WEEK.value),
        types.InlineKeyboardButton(text="Каждый месяц", callback_data=RepeatType.EVERY_MONTH.value),
        types.InlineKeyboardButton(text="Каждый год", callback_data=RepeatType.EVERY_YEAR.value),
        types.InlineKeyboardButton(text="Только сегодня", callback_data=RepeatType.ONLY_DAY.value),
        types.InlineKeyboardButton(text=config.back_text, callback_data=InlineButtonType.RETURN.value),
        types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value)]
    for InlineKeyboardButton in inline_keyboard:
        builder.row(InlineKeyboardButton)
    return builder.as_markup(resize_keyboard=True)


def priority_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    inline_keyboard = [
        types.InlineKeyboardButton(text="Низкий", callback_data=Priority.LOW.value),
        types.InlineKeyboardButton(text="Средний", callback_data=Priority.MEDIUM.value),
        types.InlineKeyboardButton(text="Высокий", callback_data=Priority.HIGH.value),
        types.InlineKeyboardButton(text="Критический", callback_data=Priority.CRITICAL.value),
    ]
    for InlineKeyboardButton in inline_keyboard:
        builder.row(InlineKeyboardButton)
    builder.row(types.InlineKeyboardButton(text=config.back_text, callback_data=InlineButtonType.RETURN.value))
    builder.row(types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value))
    return builder.as_markup(resize_keyboard=True)


def status_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Выполнить", callback_data=Status.TO_DO.value))
    builder.add(types.InlineKeyboardButton(text="В процессе", callback_data=Status.PROCESSING.value))
    builder.add(types.InlineKeyboardButton(text="Выполнено", callback_data=Status.DONE.value))
    builder.row(types.InlineKeyboardButton(text=config.back_text, callback_data=InlineButtonType.RETURN.value),
                types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value),
                width=8)
    return builder.as_markup(resize_keyboard=True)


def private_events_list_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="По статусу", callback_data='status'))
    builder.add(types.InlineKeyboardButton(text="По приоритету", callback_data='priority'))
    builder.add(types.InlineKeyboardButton(text="Все", callback_data="all"))
    builder.row(types.InlineKeyboardButton(text="Групповые", callback_data="group"))
    builder.row(types.InlineKeyboardButton(text="Личный чат", callback_data="private"))
    builder.row(
        types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value), width=8)
    return builder.as_markup(resize_keyboard=True)


def group_events_list_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="По статусу", callback_data='status'))
    builder.add(types.InlineKeyboardButton(text="По приоритету", callback_data='priority'))
    builder.add(types.InlineKeyboardButton(text="Все", callback_data="all"))
    builder.row(
        types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value), width=8)
    return builder.as_markup(resize_keyboard=True)


def chat_type_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="В этот чат", callback_data=Chat.PRIVATE.value)
    )
    builder.row(
        types.InlineKeyboardButton(text="В группу (бот должен там быть)", callback_data=Chat.GROUP.value)
    )
    builder.row(types.InlineKeyboardButton(text=config.back_text, callback_data=InlineButtonType.RETURN.value),
                types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value),
                width=8)
    return builder.as_markup(resize_keyboard=True)


def delete_type_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Все", callback_data=DeleteEvent.DELETE_ALL.value),
    )
    builder.row(
        types.InlineKeyboardButton(text="Отдельные", callback_data=DeleteEvent.DELETE.value)
    )
    builder.row(types.InlineKeyboardButton(text=config.cancel_title, callback_data=InlineButtonType.CANCEL.value),
                width=8)
    return builder.as_markup(resize_keyboard=True)


def get_event_delete_keyboard(event_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Изменить",
                    callback_data=f"update_event:{event_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Удалить",
                    callback_data=f"delete_event:{event_id}"
                )
            ]
        ]
    )

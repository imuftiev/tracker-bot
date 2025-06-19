from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types

import config
from const.event_status import EventStatus
from const.priority_status import PriorityStatus
from const.repeatable_type import RepeatType, RepeatDays

config = config.BotConfig()


def get_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="1")
    kb.button(text="2")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def cancel_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=config.cancel_title, callback_data="cancel"))
    return builder.as_markup(resize_keyboard=True)


def cancel_back_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=config.back_text, callback_data="back"))
    builder.row(types.InlineKeyboardButton(text=config.cancel_title, callback_data="cancel"))
    return builder.as_markup(resize_keyboard=True)


def choose_day_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    inline_keyboard = [
        types.InlineKeyboardButton(text="Все дни недели", callback_data=RepeatDays.ALL_DAYS.value),
        types.InlineKeyboardButton(text="В конкретные дни", callback_data=RepeatDays.EXACT_DAY.value),
    ]
    for InlineKeyboardButton in inline_keyboard:
        builder.row(InlineKeyboardButton, width=8)
    return builder.as_markup(resize_keyboard=True)


def repeatable_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    inline_keyboard = [
        types.InlineKeyboardButton(text="Каждый день", callback_data=RepeatType.EVERY_DAY.value),
        types.InlineKeyboardButton(text="Каждую неделю", callback_data=RepeatType.EVERY_WEEK.value),
        types.InlineKeyboardButton(text="Каждый месяц", callback_data=RepeatType.EVERY_MONTH.value),
        types.InlineKeyboardButton(text="Каждый год", callback_data=RepeatType.EVERY_YEAR.value),
        types.InlineKeyboardButton(text="Только сегодня", callback_data=RepeatType.ONLY_DAY.value),
        types.InlineKeyboardButton(text="Определенный день", callback_data=RepeatType.IN_PARTICULAR_DAY.value),
        types.InlineKeyboardButton(text=config.back_text, callback_data="back"),
        types.InlineKeyboardButton(text=config.cancel_title, callback_data="cancel")]
    for InlineKeyboardButton in inline_keyboard:
        builder.row(InlineKeyboardButton)
    return builder.as_markup(resize_keyboard=True)


def priority_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    inline_keyboard = [
        types.InlineKeyboardButton(text="Низкий", callback_data=PriorityStatus.CRITICAL.value),
        types.InlineKeyboardButton(text="Средний", callback_data=PriorityStatus.HIGH.value),
        types.InlineKeyboardButton(text="Высокий", callback_data=PriorityStatus.MEDIUM.value),
        types.InlineKeyboardButton(text="Критический", callback_data=PriorityStatus.LOW.value),
    ]
    for InlineKeyboardButton in inline_keyboard:
        builder.row(InlineKeyboardButton)
    builder.row(types.InlineKeyboardButton(text=config.cancel_title, callback_data="cancel"))
    return builder.as_markup(resize_keyboard=True)


def status_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Выполнить", callback_data=EventStatus.TO_DO.value))
    builder.add(types.InlineKeyboardButton(text="В процессе", callback_data=EventStatus.PROCESSING.value))
    builder.add(types.InlineKeyboardButton(text="Выполнено", callback_data=EventStatus.DONE.value))
    builder.row(types.InlineKeyboardButton(text=config.back_text, callback_data="back"),
                types.InlineKeyboardButton(text=config.cancel_title, callback_data="cancel"),width=8)
    return builder.as_markup(resize_keyboard=True)

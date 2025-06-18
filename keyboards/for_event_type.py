from tkinter import EventType

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types

from const.event_status import EventStatus
from const.priority_status import PriorityStatus


def get_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="1")
    kb.button(text="2")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def cancel_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Cancel", callback_data="cancel"))
    return builder.as_markup(resize_keyboard=True)


def repeatable_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    inline_keyboard = [
        types.InlineKeyboardButton(text="Каждый день", callback_data="EVERY_DAY"),
        types.InlineKeyboardButton(text="Каждую неделю", callback_data="EVERY_WEEK"),
        types.InlineKeyboardButton(text="Каждый месяц", callback_data="EVERY_MONTH"),
        types.InlineKeyboardButton(text="Каждый год", callback_data="EVERY_YEAR"),
        types.InlineKeyboardButton(text="Только сегодня", callback_data="ONLY_TODAY"),
        types.InlineKeyboardButton(text="В определенный день", callback_data="O"),
        types.InlineKeyboardButton(text="Отмена", callback_data="cancel")]
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
        types.InlineKeyboardButton(text="Отмена", callback_data="cancel")
    ]
    for InlineKeyboardButton in inline_keyboard:
        builder.row(InlineKeyboardButton)
    return builder.as_markup(resize_keyboard=True)


def status_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Выполнить", callback_data=EventStatus.TO_DO.value))
    builder.add(types.InlineKeyboardButton(text="В процессе", callback_data=EventStatus.PROCESSING.value))
    builder.add(types.InlineKeyboardButton(text="Выполнено", callback_data=EventStatus.DONE.value))
    builder.add(types.InlineKeyboardButton(text="Отмена", callback_data='cancel'))
    return builder.as_markup(resize_keyboard=True)

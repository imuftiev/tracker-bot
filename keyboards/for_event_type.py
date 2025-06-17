from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types


def get_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="1")
    kb.button(text="2")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def repeatable_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Каждый день", callback_data="EVERY_DAY"))
    builder.add(types.InlineKeyboardButton(text="Каждую неделю", callback_data="EVERY_WEEK"))
    builder.add(types.InlineKeyboardButton(text="Каждый месяц", callback_data="EVERY_MONTH"))
    builder.add(types.InlineKeyboardButton(text="Каждый год", callback_data="EVERY_YEAR"))
    return builder.as_markup(resize_keyboard=True)


def priority_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Низкий", callback_data='LOW'))
    builder.add(types.InlineKeyboardButton(text="Средний", callback_data='MEDIUM'))
    builder.add(types.InlineKeyboardButton(text="Высокий", callback_data='HIGH'))
    builder.add(types.InlineKeyboardButton(text="Критический", callback_data='CRITICAL'))
    return builder.as_markup(resize_keyboard=True)


def status_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Выполнить", callback_data='TO_DO'))
    builder.add(types.InlineKeyboardButton(text="В процессе", callback_data='PROCESSING'))
    builder.add(types.InlineKeyboardButton(text="Выполнено", callback_data='DONE'))
    return builder.as_markup(resize_keyboard=True)

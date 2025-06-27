import logging
from datetime import datetime, time
from aiogram.types import Message, InlineKeyboardMarkup

from keyboards.keyboards import get_cancel_return_keyboard


async def set_time_remind(message: Message) -> datetime | None:
    try:
        time_input = message.text.strip()

        if ":" in time_input:
            time_obj = datetime.strptime(time_input, "%H:%M").time()
        elif time_input.isdigit() and len(time_input) == 4:
            time_obj = datetime.strptime(time_input, "%H%M").time()
        else:
            raise ValueError("Введен неверный формат времени.")

        now = datetime.now()
        remind_time = datetime.combine(now.date(), time_obj)

        if remind_time < now:
            remind_time = remind_time.replace(day=now.day + 1)

        return remind_time

    except Exception as e:
        logging.error(f"[set_time_remind] {e}")
        await message.answer("❌ Неверный формат времени. Введите в формате 12:30 или 1230.")
        return None

async def set_date_remind(message: Message) -> datetime | None:
    try:
        date_input = message.text.strip()

        if " " in date_input:
            date_part, time_part = date_input.split(" ")
            dt = datetime.strptime(f"{date_part} {time_part}", "%d.%m.%Y %H:%M")
            return dt

        elif ":" in date_input and len(date_input) <= 5:
            t = datetime.strptime(date_input, "%H:%M").time()
            now = datetime.now()
            dt = datetime.combine(now.date(), t)
            return dt

        elif "." in date_input:
            d = datetime.strptime(date_input, "%d.%m.%Y").date()
            dt = datetime.combine(d, time(hour=8, minute=0))
            return dt

        else:
            raise ValueError("Неверный формат даты/времени.")


    except Exception as e:
        logging.error(f"[Ошибка парсинга даты]: {e}")
        await message.answer("❌ Неверный формат времени. Введите в формате «Месяц.День.Год Часы:Минуты»\nПример: «14.08.2025 09:00»",
                             reply_markup=get_cancel_return_keyboard())
        return None


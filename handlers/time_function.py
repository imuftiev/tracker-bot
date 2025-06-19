import logging
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


async def set_time_remind(message: Message, state : FSMContext) -> datetime | None:
    try:
        time_input = message.text.strip()

        if ":" in time_input:
            time_obj = datetime.strptime(time_input, "%H:%M").time()
        elif time_input.isdigit() and len(time_input) == 4:
            time_obj = datetime.strptime(time_input, "%H%M").time()
        else:
            raise ValueError("Введен неверны формат времени.")

        now = datetime.now()
        remind_time = datetime.combine(now.date(), time_obj)

        if remind_time < now:
            remind_time = remind_time.replace(day=now.day + 1)

        return remind_time

    except Exception as e:
        logging.error(f"[set_time_remind] {e}")
        await message.answer("❌ Неверный формат времени. Введите в формате 12:30 или 1230.")
        return None

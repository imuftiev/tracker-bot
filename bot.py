import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from config import BotConfig
from db import Event
from handlers import start_handler, help_handler, add_handler
from handlers import reminder_worker as rw
from handlers import daily_remind_worker as drw

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher()
botconfig = BotConfig()
event = Event()

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_routers(start_handler.router, help_handler.router, add_handler.router)
    asyncio.create_task(rw.reminder_worker(bot))
    asyncio.create_task(drw.daily_reminder_worker(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

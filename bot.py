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
from handlers.base import start, help, event_list, add, default, change_event, delete
from handlers.reminders import scheduled as rw
from handlers.keyboard import inline

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher()
botconfig = BotConfig()
event = Event()


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_routers(start.router, help.router,
                       add.router, event_list.router,
                       delete.router, change_event.router,
                       inline.router, default.router)
    asyncio.create_task(rw.reminder_worker(bot))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

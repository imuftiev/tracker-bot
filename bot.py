import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from config import BotConfig
from handlers.base import start, help, list, add, default, update, delete, group_chat, private_chat, link, groups
from handlers.keyboard import inline
from scheduler.apscheduler import load_all_events, scheduler

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher()
botconfig = BotConfig()


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_routers(start.router, help.router, add.router, link.router, groups.router, inline.router,
                       private_chat.router, group_chat.router,
                       list.router, update.router, default.router, delete.router)
    scheduler.start()
    await load_all_events()
    print("[Scheduler] Текущие задачи:")
    scheduler.print_jobs()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

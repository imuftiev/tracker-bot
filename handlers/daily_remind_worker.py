import asyncio
from datetime import datetime, timezone

from sqlalchemy import Time
from sqlalchemy.orm import sessionmaker
from db import engine, Event
from aiogram import Bot

Session = sessionmaker(bind=engine)


async def daily_reminder_worker(bot: Bot):
    while True:
        try:
            now = datetime.now().time().replace(second=0, microsecond=0)
            with Session() as session:
                events = session.query(Event).filter(
                    Event.remind_at.cast(Time) == now,
                    Event.repeatable == True
                ).all()

                for event in events:
                    await bot.send_message(
                        chat_id=event.telegram_chat_id,
                        text=(f"🔔<strong> Ежедневное событие: </strong> <i>{event.title}</i>\n"
                              f"📝<strong> Описание: </strong> <i>{event.description}</i>\n"
                              f"❓<strong> Статус: </strong> <i>{event.status.value}</i>\n"
                              f"✔️<strong> Приоритет: </strong> <i>{event.priority.value}</i>\n"),
                        parse_mode="HTML"
                    )

                    event.sent = True
                    session.add(event)

                session.commit()

        except Exception as e:
            print(f"[ReminderWorker] Ошибка: {e}")

        await asyncio.sleep(60)

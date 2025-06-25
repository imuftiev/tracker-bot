import asyncio
from sqlalchemy.orm import sessionmaker

from const.event.repeatable import RepeatType
from db import engine, Event, Group
from aiogram import Bot

Session = sessionmaker(bind=engine)

from datetime import datetime, timezone


def match_event_repeat(event: Event, now: datetime) -> bool:
    event_time = event.remind_time
    if not event_time:
        return False

    same_time = now.time().hour == event_time.hour and now.time().minute == event_time.minute

    if not same_time:
        return False

    if event.repeat_type == RepeatType.ONLY_DAY:
        return now.date() == event.remind_at.date()

    elif event.repeat_type == RepeatType.EVERY_DAY:
        return True

    elif event.repeat_type == RepeatType.EVERY_WEEK:
        # days_of_week: ['monday', 'friday']
        weekday = now.strftime("%A").lower()
        return event.days_of_week and weekday in [d.lower() for d in event.days_of_week]

    elif event.repeat_type == RepeatType.EVERY_MONTH:
        # Напоминания по числу месяца
        return now.day == event.remind_at.day

    elif event.repeat_type == RepeatType.EVERY_YEAR:
        return now.day == event.remind_at.day and now.month == event.remind_at.month

    return False


async def reminder_worker(bot: Bot):
    while True:
        try:
            now = datetime.now(timezone.utc)
            with Session() as session:
                events = session.query(Event).filter(
                    Event.remind_at <= now,
                    Event.sent == False
                ).all()

                for event in events:
                    if event.repeat_type == RepeatType.EVERY_WEEK:
                        weekday = datetime.now().strftime("%A").lower()

                        if not event.days_of_week or weekday not in event.days_of_week:
                            continue

                    chat_id = None
                    if event.group_id:
                        group = session.query(Group).filter_by(id=event.group_id).first()
                        if group:
                            chat_id = group.telegram_group_id
                    else:
                        chat_id = event.telegram_chat_id

                    if chat_id:
                        await bot.send_message(
                            chat_id=chat_id,
                            text=str(event),
                            parse_mode="HTML"
                        )

                        if not event.repeatable:
                            event.sent = True

                        session.add(event)

                session.commit()

        except Exception as e:
            print(f"[ReminderWorker] Ошибка: {e}")

        await asyncio.sleep(30)

import logging
import os
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from aiogram import Bot

from const.event.repeatable import RepeatType
from db import Event, Group

DATABASE_URL = os.getenv('DATABASE_URL')
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
BOT_TOKEN = os.getenv('BOT_TOKEN')

engine = create_async_engine(ASYNC_DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

bot = Bot(token=BOT_TOKEN)

scheduler = AsyncIOScheduler(
    jobstores={'default': SQLAlchemyJobStore(url=DATABASE_URL)}
)

moscow_tz = ZoneInfo("Europe/Moscow")

DAY_OF_WEEK_MAP = {
    'Понедельник': 'mon',
    'Вторник': 'tue',
    'Среда': 'wed',
    'Четверг': 'thu',
    'Пятница': 'fri',
    'Суббота': 'sat',
    'Воскресенье': 'sun',
    'Все дни': '*'
}

from sqlalchemy.future import select


async def send_reminder(event_id: int):
    logging.info(f"[Reminder] Вызван send_reminder для события {event_id}")

    async with AsyncSessionLocal() as session:
        result = await session.get(Event, event_id)
        event = result

        if not event:
            logging.warning(f"[Reminder] Событие {event_id} не найдено")
            return

        chat_id = None

        if event.group_id:
            stmt = select(Group).filter_by(id=event.group_id)
            group_result = await session.execute(stmt)
            group = group_result.scalar_one_or_none()

            if group:
                chat_id = group.telegram_group_id
            else:
                logging.warning(f"[Reminder] Группа с id={event.group_id} не найдена")
        else:
            chat_id = event.telegram_chat_id

        try:
            await bot.send_message(chat_id, str(event), parse_mode="HTML")
        except Exception as e:
            logging.error(f"[Reminder] Ошибка отправки: {e}")

        if not event.repeatable:
            event.sent = True
            await session.delete(event)
            try:
                scheduler.remove_job(f"event_{event_id}")
            except JobLookupError:
                pass

            for suffix in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', '*']:
                try:
                    scheduler.remove_job(f"event_{event_id}_{suffix}")
                except JobLookupError:
                    continue
            await session.commit()


def schedule_one_time_event(event: Event):
    if event.sent:
        return

    now_utc = datetime.now(timezone.utc)
    run_time_utc = event.remind_at

    if run_time_utc.tzinfo is None:
        run_time_utc = run_time_utc.replace(tzinfo=moscow_tz).astimezone(timezone.utc)

    run_time_msk = run_time_utc.astimezone(moscow_tz)
    now_msk = now_utc.astimezone(moscow_tz)

    logging.info(f"[Scheduler] Проверка события {event.id}: remind_at (MSK)={run_time_msk}, now (MSK)={now_msk}")

    if run_time_utc < now_utc and (now_utc - run_time_utc) > timedelta(seconds=60):
        logging.info(f"[Scheduler] Пропущено событие {event.id}, слишком поздно запускать.")
        return

    scheduler.add_job(
        send_reminder,
        trigger=DateTrigger(run_date=run_time_utc, timezone=timezone.utc),
        args=[event.id],
        id=f"event_{event.id}",
        replace_existing=True,
        misfire_grace_time=60
    )
    logging.info(f"[Scheduler] Одноразовое событие: {event.id} на {run_time_msk} (MSK)")


def schedule_repeatable_event(event: Event):
    if event.repeat_type == RepeatType.EVERY_YEAR and event.days_of_month and event.month:
        for month in event.month:
            for day in event.days_of_month:
                scheduler.add_job(
                    send_reminder,
                    trigger=CronTrigger(
                        month=month,
                        day=day,
                        hour=event.remind_time.hour,
                        minute=event.remind_time.minute,
                        timezone=moscow_tz
                    ),
                    args=[event.id],
                    id=f"event_{event.id}_m{month}_d{day}",
                    replace_existing=True,
                    misfire_grace_time=60
                )
    if event.repeat_type == RepeatType.EVERY_MONTH and event.days_of_month:
        for day in event.days_of_month:
            if not (1 <= day <= 31):
                logging.warning(f"[Scheduler] Неверный день месяца: {day}")
                continue

            scheduler.add_job(
                send_reminder,
                trigger=CronTrigger(
                    day=day,
                    hour=event.remind_time.hour,
                    minute=event.remind_time.minute,
                    timezone=moscow_tz
                ),
                args=[event.id],
                id=f"event_{event.id}_day{day}",
                replace_existing=True,
                misfire_grace_time=60
            )
            logging.info(f"[Scheduler] Повторяемое событие: {event.id} - каждый {day} числа в {event.remind_time} МСК")

    if event.repeat_type == RepeatType.EVERY_WEEK and event.days_of_week:
        for weekday in event.days_of_week:
            cron_day = DAY_OF_WEEK_MAP.get(weekday)
            if not cron_day:
                logging.warning(f"[Scheduler] Неизвестный день недели: {weekday}")
                continue

            scheduler.add_job(
                send_reminder,
                trigger=CronTrigger(
                    day_of_week=cron_day,
                    hour=event.remind_time.hour,
                    minute=event.remind_time.minute,
                    timezone=moscow_tz
                ),
                args=[event.id],
                id=f"event_{event.id}_{cron_day}",
                replace_existing=True,
                misfire_grace_time=60
            )
            logging.info(f"[Scheduler] Повторяемое событие: {event.id} в {cron_day} - {event.remind_time} МСК")


async def load_all_events():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Event))
        events = result.scalars().all()
        for event in events:
            if event.repeatable:
                schedule_repeatable_event(event)
            else:
                schedule_one_time_event(event)

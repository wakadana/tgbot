from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot

from bot.handlers.digest import collect_items, format_digest
from bot.database.db import get_user_interests, DB_PATH
from bot.filters.content_filter import ContentFilter

# Глобальная переменная для планировщика
SCHEDULER = None


def parse_time_str(time_str: str) -> Optional[tuple]:
    try:
        hh, mm = time_str.split(":")
        h = int(hh)
        m = int(mm)
        if 0 <= h < 24 and 0 <= m < 60:
            return h, m
    except Exception:
        return None
    return None


async def send_scheduled_digest(bot: Bot, user_id: int, chat_id: int):
    items = await collect_items(user_id)
    interests = await get_user_interests(user_id)
    interests_list = [i['interest_text'] for i in interests]
    filtered = ContentFilter().filter_by_interests(items, interests_list)
    text = format_digest(filtered)
    await bot.send_message(chat_id, text, parse_mode="Markdown")


def setup_user_schedule(scheduler: AsyncIOScheduler, bot: Bot, user_id: int, chat_id: int, time_str: Optional[str]):
    # Remove previous job if exists
    job_id = f"digest_{user_id}"
    try:
        job = scheduler.get_job(job_id)
        if job:
            scheduler.remove_job(job_id)
    except Exception:
        pass

    if not time_str:
        return

    hm = parse_time_str(time_str)
    if not hm:
        return
    hour, minute = hm

    trigger = CronTrigger(hour=hour, minute=minute)
    scheduler.add_job(
        send_scheduled_digest,
        id=job_id,
        trigger=trigger,
        kwargs={"bot": bot, "user_id": user_id, "chat_id": chat_id},
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )



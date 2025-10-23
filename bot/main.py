import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot.config import load_config
from bot.database.db import init_db, get_user
from bot.handlers.start import start_router
from bot.handlers.sources import sources_router
from bot.handlers.interests import interests_router
from bot.handlers.digest import digest_router
from bot.handlers.schedule import schedule_router
from bot.scheduler.tasks import setup_user_schedule
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def main():
    config = load_config()

    logging.basicConfig(level=getattr(logging, config.log_level.upper(), logging.INFO))

    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    # Shared context - сохраняем в глобальных переменных
    import bot.database.db as db_module
    import bot.scheduler.tasks as scheduler_module
    db_module.DB_PATH = config.database_path
    scheduler_module.SCHEDULER = AsyncIOScheduler()
    scheduler_module.SCHEDULER.start()

    # Init DB
    await init_db(config.database_path)

    # Register routers
    dp.include_router(start_router)
    dp.include_router(sources_router)
    dp.include_router(interests_router)
    dp.include_router(digest_router)
    dp.include_router(schedule_router)

    # Restore existing user schedules
    import aiosqlite
    async with aiosqlite.connect(config.database_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE schedule IS NOT NULL") as cursor:
            async for row in cursor:
                setup_user_schedule(
                    scheduler=scheduler_module.SCHEDULER,
                    bot=bot,
                    user_id=row['user_id'],
                    chat_id=row['chat_id'],
                    time_str=row['schedule'],
                )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())



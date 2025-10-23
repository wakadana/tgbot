from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.inline import get_schedule_menu, get_main_menu
from bot.database.db import update_schedule, get_user, DB_PATH
from bot.scheduler.tasks import setup_user_schedule


schedule_router = Router()


@schedule_router.callback_query(F.data == "menu:schedule")
async def open_schedule_menu(callback: CallbackQuery):
    await callback.message.edit_text("Настройте время авто-дайджеста:", reply_markup=get_schedule_menu())
    await callback.answer()


@schedule_router.callback_query(F.data == "schedule:off")
async def schedule_off(callback: CallbackQuery):
    await update_schedule(callback.from_user.id, None)
    await callback.message.edit_text("Автоматическая отправка отключена.", reply_markup=get_main_menu())
    await callback.answer()


@schedule_router.callback_query(F.data.startswith("schedule:set:"))
async def schedule_set(callback: CallbackQuery):
    time_str = callback.data.split(":", 2)[-1]
    await update_schedule(callback.from_user.id, time_str)
    # Создать/обновить задачу в планировщике
    user = await get_user(callback.from_user.id)
    if user:
        from bot.scheduler.tasks import setup_user_schedule, SCHEDULER
        setup_user_schedule(
            scheduler=SCHEDULER,
            bot=callback.bot,
            user_id=callback.from_user.id,
            chat_id=user['chat_id'],
            time_str=time_str,
        )
    await callback.message.edit_text(f"Расписание установлено: {time_str}", reply_markup=get_main_menu())
    await callback.answer()



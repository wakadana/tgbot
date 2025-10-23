from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from bot.keyboards.inline import get_main_menu
from bot.database.db import add_user

start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: types.Message):
    await add_user(user_id=message.from_user.id, chat_id=message.chat.id)
    await message.answer(
        "Привет! Я помогу собирать новости из ваших источников и интересов.\n"
        "Используйте меню ниже, чтобы настроить источники, интересы и расписание.",
        reply_markup=get_main_menu(),
    )


@start_router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "Команды:\n"
        "/start — запуск и главное меню\n"
        "/help — помощь\n"
        "/digest — сгенерировать дайджест сейчас\n\n"
        "Используйте кнопки для добавления источников, тем и расписания.",
        reply_markup=get_main_menu(),
    )


@start_router.callback_query(F.data == "menu:root")
async def back_to_main(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=get_main_menu(),
        )
    except Exception:
        # Если не удается отредактировать, отправляем новое сообщение
        await callback.message.answer(
            "Главное меню:",
            reply_markup=get_main_menu(),
        )
    await callback.answer()



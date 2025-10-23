from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline import get_sources_menu, get_source_list_keyboard
from bot.database.db import add_source, get_user_sources, delete_source
from bot.parsers.telegram_parser import validate_telegram_channel
from bot.config import load_config


sources_router = Router()


class AddSourceFSM(StatesGroup):
    waiting_url = State()
    waiting_telegram_url = State()


@sources_router.callback_query(F.data == "menu:sources")
async def open_sources_menu(callback: CallbackQuery):
    await callback.message.edit_text("Меню источников:", reply_markup=get_sources_menu())
    await callback.answer()


@sources_router.callback_query(F.data == "sources:list")
async def list_sources(callback: CallbackQuery):
    sources = await get_user_sources(callback.from_user.id)
    if not sources:
        try:
            await callback.message.edit_text("У вас пока нет источников.", reply_markup=get_sources_menu())
        except Exception:
            await callback.message.answer("У вас пока нет источников.", reply_markup=get_sources_menu())
        return await callback.answer()
    
    try:
        await callback.message.edit_text("Ваши источники:", reply_markup=get_source_list_keyboard(sources))
    except Exception:
        await callback.message.answer("Ваши источники:", reply_markup=get_source_list_keyboard(sources))
    await callback.answer()


@sources_router.callback_query(F.data == "sources:add_telegram")
async def add_telegram_start(callback: CallbackQuery, state: FSMContext):
    config = load_config()
    if not config.api_id or not config.api_hash:
        await callback.message.edit_text(
            "❌ Telegram API не настроен!\n\n"
            "Для парсинга Telegram-каналов необходимо:\n"
            "1. Зайти на https://my.telegram.org\n"
            "2. Создать приложение и получить API_ID, API_HASH\n"
            "3. Указать их в файле .env\n\n"
            "Пока что используйте RSS или веб-сайты.",
            reply_markup=get_sources_menu()
        )
        return await callback.answer()

    await state.set_state(AddSourceFSM.waiting_telegram_url)
    await callback.message.edit_text(
        "📱 Отправьте ссылку на Telegram-канал:\n\n"
        "Примеры:\n"
        "• @channel_name\n"
        "• https://t.me/channel_name\n"
        "• t.me/channel_name\n\n"
        "⚠️ **Внимание:** При первом добавлении канала потребуется авторизация в Telegram API."
    )
    await callback.answer()


@sources_router.callback_query(F.data == "sources:add_rss")
async def add_rss_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddSourceFSM.waiting_url)
    await callback.message.edit_text("Отправьте URL RSS-ленты:")
    await callback.answer()


@sources_router.callback_query(F.data == "sources:add_web")
async def add_web_start(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type='website')
    await state.set_state(AddSourceFSM.waiting_url)
    await callback.message.edit_text("Отправьте URL сайта:")
    await callback.answer()


@sources_router.message(AddSourceFSM.waiting_telegram_url)
async def receive_telegram_url(message: types.Message, state: FSMContext):
    url = message.text.strip()
    config = load_config()
    
    # Нормализуем URL
    if url.startswith("https://t.me/"):
        url = url.replace("https://t.me/", "@")
    elif url.startswith("t.me/"):
        url = "@" + url.replace("t.me/", "")
    elif not url.startswith("@"):
        url = "@" + url
    
    # Валидация канала
    try:
        is_valid = await validate_telegram_channel(
            url, 
            config.api_id, 
            config.api_hash, 
            config.phone_number
        )
        
        if not is_valid:
            await message.answer(
                "❌ Канал недоступен или не существует!\n\n"
                "Проверьте:\n"
                "• Правильность ссылки\n"
                "• Публичность канала\n"
                "• Наличие прав на чтение\n\n"
                "Попробуйте другую ссылку:",
                reply_markup=get_sources_menu()
            )
            await state.clear()
            return
        
        # Добавляем источник
        await add_source(message.from_user.id, 'telegram', url)
        await state.clear()
        await message.answer(f"✅ Telegram-канал {url} добавлен!", reply_markup=get_sources_menu())
        
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при проверке канала: {str(e)}\n\n"
            "Попробуйте позже или используйте RSS/веб-сайты.",
            reply_markup=get_sources_menu()
        )
        await state.clear()


@sources_router.message(AddSourceFSM.waiting_url)
async def receive_source_url(message: types.Message, state: FSMContext):
    url = message.text.strip()
    data = await state.get_data()
    type_ = data.get('type')
    if not (url.startswith("http://") or url.startswith("https://")):
        return await message.answer("Пожалуйста, отправьте корректный URL, начинающийся с http(s)://")
    # Простая валидация; детальную проверку делаем на этапе парсинга
    await add_source(message.from_user.id, type_, url)
    await state.clear()
    await message.answer("Источник добавлен!", reply_markup=get_sources_menu())


@sources_router.callback_query(F.data.startswith("sources:del:"))
async def delete_source_cb(callback: CallbackQuery):
    try:
        source_id = int(callback.data.split(":")[-1])
    except ValueError:
        return await callback.answer("Некорректный идентификатор", show_alert=True)
    await delete_source(source_id, callback.from_user.id)
    sources = await get_user_sources(callback.from_user.id)
    text = "Источник удален."
    try:
        if sources:
            await callback.message.edit_text(text, reply_markup=get_source_list_keyboard(sources))
        else:
            await callback.message.edit_text(text + "\nУ вас больше нет источников.", reply_markup=get_sources_menu())
    except Exception:
        if sources:
            await callback.message.answer(text, reply_markup=get_source_list_keyboard(sources))
        else:
            await callback.message.answer(text + "\nУ вас больше нет источников.", reply_markup=get_sources_menu())
    await callback.answer()



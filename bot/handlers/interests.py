from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline import get_interests_menu, get_interest_list_keyboard, get_popular_topics_keyboard
from bot.database.db import add_interest, get_user_interests, delete_interest


interests_router = Router()


class AddInterestFSM(StatesGroup):
    waiting_text = State()


@interests_router.callback_query(F.data == "menu:interests")
async def open_interests_menu(callback: CallbackQuery):
    await callback.message.edit_text("Меню интересов:", reply_markup=get_interests_menu())
    await callback.answer()


@interests_router.callback_query(F.data == "interests:list")
async def list_interests(callback: CallbackQuery):
    interests = await get_user_interests(callback.from_user.id)
    if not interests:
        try:
            await callback.message.edit_text("У вас пока нет тем интересов.", reply_markup=get_interests_menu())
        except Exception:
            await callback.message.answer("У вас пока нет тем интересов.", reply_markup=get_interests_menu())
        return await callback.answer()
    
    try:
        await callback.message.edit_text("Ваши темы интересов:", reply_markup=get_interest_list_keyboard(interests))
    except Exception:
        await callback.message.answer("Ваши темы интересов:", reply_markup=get_interest_list_keyboard(interests))
    await callback.answer()


@interests_router.callback_query(F.data == "interests:add")
async def add_interest_start(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.edit_text(
            "Выберите популярную тематику или введите свою:",
            reply_markup=get_popular_topics_keyboard()
        )
    except Exception:
        await callback.message.answer(
            "Выберите популярную тематику или введите свою:",
            reply_markup=get_popular_topics_keyboard()
        )
    await callback.answer()


# Словарь популярных тем
POPULAR_TOPICS = {
    "tech": "💻 Технологии",
    "ai": "🤖 ИИ и машинное обучение", 
    "mobile": "📱 Мобильные приложения",
    "crypto": "💰 Криптовалюты",
    "stocks": "📈 Фондовый рынок",
    "finance": "🏦 Банки и финансы",
    "politics": "🏛️ Политика",
    "world": "🌍 Международные новости",
    "law": "⚖️ Право и законы",
    "science": "🔬 Наука",
    "medicine": "🏥 Медицина",
    "ecology": "🌱 Экология",
    "sports": "⚽ Спорт",
    "movies": "🎬 Кино и сериалы",
    "gaming": "🎮 Игры",
    "startups": "🚀 Стартапы",
    "business": "💼 Бизнес",
    "ecommerce": "🛒 E-commerce"
}

@interests_router.callback_query(F.data.startswith("topic:"))
async def select_popular_topic(callback: CallbackQuery):
    topic_key = callback.data.split(":", 1)[1]
    if topic_key in POPULAR_TOPICS:
        topic_text = POPULAR_TOPICS[topic_key]
        await add_interest(callback.from_user.id, topic_text)
        try:
            await callback.message.edit_text(
                f"✅ Тема '{topic_text}' добавлена!\n\nВыберите еще одну тему или вернитесь в меню:",
                reply_markup=get_popular_topics_keyboard()
            )
        except Exception:
            await callback.message.answer(
                f"✅ Тема '{topic_text}' добавлена!\n\nВыберите еще одну тему или вернитесь в меню:",
                reply_markup=get_popular_topics_keyboard()
            )
    await callback.answer()


@interests_router.callback_query(F.data == "interests:add_manual")
async def add_interest_manual(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddInterestFSM.waiting_text)
    try:
        await callback.message.edit_text("Отправьте текст темы/ключевых слов (до 100 символов):")
    except Exception:
        await callback.message.answer("Отправьте текст темы/ключевых слов (до 100 символов):")
    await callback.answer()


@interests_router.message(AddInterestFSM.waiting_text)
async def receive_interest_text(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text or len(text) > 100:
        return await message.answer("Введите непустой текст до 100 символов.")
    await add_interest(message.from_user.id, text)
    await state.clear()
    await message.answer("Тема добавлена!", reply_markup=get_interests_menu())


@interests_router.callback_query(F.data.startswith("interests:del:"))
async def delete_interest_cb(callback: CallbackQuery):
    try:
        interest_id = int(callback.data.split(":")[-1])
    except ValueError:
        return await callback.answer("Некорректный идентификатор", show_alert=True)
    await delete_interest(interest_id, callback.from_user.id)
    interests = await get_user_interests(callback.from_user.id)
    text = "Тема удалена."
    try:
        if interests:
            await callback.message.edit_text(text, reply_markup=get_interest_list_keyboard(interests))
        else:
            await callback.message.edit_text(text + "\nУ вас больше нет тем.", reply_markup=get_interests_menu())
    except Exception:
        if interests:
            await callback.message.answer(text, reply_markup=get_interest_list_keyboard(interests))
        else:
            await callback.message.answer(text + "\nУ вас больше нет тем.", reply_markup=get_interests_menu())
    await callback.answer()



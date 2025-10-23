from typing import List, Dict
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from bot.database.db import get_user_sources, get_user_interests
from bot.parsers.rss_parser import RSSParser
from bot.parsers.web_parser import WebParser
from bot.parsers.telegram_parser import parse_telegram_channel
from bot.config import load_config
from bot.filters.content_filter import ContentFilter
from bot.keyboards.inline import get_digest_actions


digest_router = Router()


async def collect_items(user_id: int) -> List[Dict]:
    sources = await get_user_sources(user_id)
    if not sources:
        return []

    rss = RSSParser()
    web = WebParser()
    config = load_config()
    items: List[Dict] = []
    
    for s in sources:
        url = s["url"]
        try:
            if s["type"] == "rss":
                items.extend(await rss.parse_feed(url))
            elif s["type"] == "website":
                items.extend(await web.parse_page(url))
            elif s["type"] == "telegram":
                # Парсим Telegram-канал
                if config.api_id and config.api_hash and config.phone_number:
                    telegram_items = await parse_telegram_channel(
                        url,
                        config.api_id,
                        config.api_hash,
                        config.phone_number,
                        limit=20  # Ограничиваем количество сообщений
                    )
                    items.extend(telegram_items)
                else:
                    print(f"Telegram API not configured, skipping {url}")
                    continue
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            continue
    
    return items


def format_digest(items: List[Dict]) -> str:
    if not items:
        return "Нет релевантных материалов по вашим интересам. Попробуйте расширить список источников или тем."
    lines = ["📰 *Ваш дайджест новостей*", ""]
    for it in items[:20]:
        title = it.get("title", "Без заголовка")
        link = it.get("link")
        source = it.get("source", "Источник")
        rel = it.get("relevance_score")
        rel_s = f"\n_Релевантность: {int(rel*100)}%_" if rel is not None else ""
        lines.append(f"🔹 *{title}*\n📌 Источник: {source}\n🔗 [Читать полностью]({link}){rel_s}\n")
    return "\n".join(lines)


@digest_router.message(Command("digest"))
async def cmd_digest(message: types.Message):
    items = await collect_items(message.from_user.id)
    interests = await get_user_interests(message.from_user.id)
    interests_list = [i['interest_text'] for i in interests]
    filtered = ContentFilter().filter_by_interests(items, interests_list)
    text = format_digest(filtered)
    await message.answer(text, reply_markup=get_digest_actions(), parse_mode="Markdown")


@digest_router.callback_query(F.data == "digest:run")
async def digest_run(callback: CallbackQuery):
    items = await collect_items(callback.from_user.id)
    interests = await get_user_interests(callback.from_user.id)
    interests_list = [i['interest_text'] for i in interests]
    filtered = ContentFilter().filter_by_interests(items, interests_list)
    text = format_digest(filtered)
    await callback.message.edit_text(text, reply_markup=get_digest_actions(), parse_mode="Markdown")
    await callback.answer()


@digest_router.callback_query(F.data == "digest:refresh")
async def digest_refresh(callback: CallbackQuery):
    return await digest_run(callback)


@digest_router.callback_query(F.data == "digest:group:topics")
async def digest_group_topics(callback: CallbackQuery):
    # MVP: просто отправим обычный дайджест (группировку можно добавить позже)
    await digest_run(callback)


@digest_router.callback_query(F.data == "digest:group:sources")
async def digest_group_sources(callback: CallbackQuery):
    await digest_run(callback)



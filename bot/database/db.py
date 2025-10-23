import aiosqlite
from typing import List, Dict, Optional, Tuple

from .models import USERS_TABLE_SQL, SOURCES_TABLE_SQL, INTERESTS_TABLE_SQL

# Глобальная переменная для пути к БД
DB_PATH = "bot_database.db"


async def init_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute(USERS_TABLE_SQL)
        await db.execute(SOURCES_TABLE_SQL)
        await db.execute(INTERESTS_TABLE_SQL)
        await db.commit()


# Users
async def add_user(user_id: int, chat_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users(user_id, chat_id) VALUES (?, ?)",
            (user_id, chat_id),
        )
        await db.commit()


async def get_user(user_id: int) -> Optional[Tuple]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def update_schedule(user_id: int, schedule: Optional[str]) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET schedule = ? WHERE user_id = ?", (schedule, user_id))
        await db.commit()


# Sources
async def add_source(user_id: int, type_: str, url: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO sources(user_id, type, url) VALUES (?, ?, ?)",
            (user_id, type_, url),
        )
        await db.commit()


async def get_user_sources(user_id: int) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM sources WHERE user_id = ? ORDER BY added_at DESC", (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def delete_source(source_id: int, user_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM sources WHERE source_id = ? AND user_id = ?", (source_id, user_id))
        await db.commit()


# Interests
async def add_interest(user_id: int, interest_text: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO interests(user_id, interest_text) VALUES (?, ?)",
            (user_id, interest_text),
        )
        await db.commit()


async def get_user_interests(user_id: int) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM interests WHERE user_id = ? ORDER BY added_at DESC", (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def delete_interest(interest_id: int, user_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM interests WHERE interest_id = ? AND user_id = ?",
            (interest_id, user_id),
        )
        await db.commit()



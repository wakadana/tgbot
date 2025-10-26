import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User
from telethon.errors import FloodWaitError, ChannelPrivateError, ChatAdminRequiredError
import random

logger = logging.getLogger(__name__)


class TelegramParser:
    def __init__(self, api_id: str, api_hash: str, phone_number: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = None
        self._session_name = "telegram_session"
        self._request_delay = 2.0  # Минимальная задержка между запросами
        self._last_request_time = 0

    async def _smart_delay(self):
        """Умная задержка между запросами с рандомизацией"""
        current_time = asyncio.get_event_loop().time()
        elapsed = current_time - self._last_request_time

        if elapsed < self._request_delay:
            delay = self._request_delay - elapsed
            # Добавляем случайность (+/- 50%)
            delay = delay * random.uniform(0.5, 1.5)
            await asyncio.sleep(delay)

        self._last_request_time = asyncio.get_event_loop().time()

    async def __aenter__(self):
        if not self.api_id or not self.api_hash:
            raise ValueError("API_ID and API_HASH are required for Telegram parsing")

        self.client = TelegramClient(self._session_name, self.api_id, self.api_hash)
        await self.client.start(phone=self.phone_number)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.disconnect()

    async def parse_channel(
            self,
            channel_url: str,
            limit: int = 50,
            max_retries: int = 3
    ) -> List[Dict]:
        """
        Парсит сообщения из Telegram-канала с защитой от бана

        Args:
            channel_url: URL или username канала
            limit: Максимальное количество сообщений (рекомендуется <= 50)
            max_retries: Максимальное количество повторных попыток

        Returns:
            Список словарей с данными сообщений
        """
        if not self.client:
            raise RuntimeError("Telegram client not initialized")

        # Ограничиваем лимит для безопасности
        limit = min(limit, 100)

        for attempt in range(max_retries):
            try:
                await self._smart_delay()

                entity = await self.client.get_entity(channel_url)

                if not isinstance(entity, (Channel, Chat)):
                    logger.warning(f"Entity {channel_url} is not a channel or chat")
                    return []

                since_date = datetime.now() - timedelta(days=7)
                messages = []

                # Добавляем задержку между итерациями
                message_count = 0
                async for message in self.client.iter_messages(
                        entity,
                        limit=limit,
                        offset_date=since_date
                ):
                    if message.text:  # Только текстовые сообщения
                        message_data = {
                            'title': self._extract_title(message.text),
                            'content': message.text,
                            'link': self._build_message_link(entity, message.id),
                            'published': message.date.isoformat(),
                            'source_name': entity.title or entity.username or "Unknown Channel",
                            'source_type': 'telegram',
                            'message_id': message.id,
                            'views': getattr(message, 'views', 0),
                            'forwards': getattr(message, 'forwards', 0)
                        }
                        messages.append(message_data)
                        message_count += 1

                        # Задержка каждые 10 сообщений
                        if message_count % 10 == 0:
                            await asyncio.sleep(random.uniform(1, 2))

                logger.info(f"Parsed {len(messages)} messages from {channel_url}")
                return messages

            except FloodWaitError as e:
                logger.warning(f"FloodWait: {e.seconds}s on attempt {attempt + 1}/{max_retries}")

                if attempt < max_retries - 1:
                    # Увеличиваем задержку для следующих запросов
                    self._request_delay = min(self._request_delay * 2, 10.0)
                    wait_time = e.seconds + random.uniform(5, 15)
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Max retries reached for {channel_url}")
                    return []

            except (ChannelPrivateError, ChatAdminRequiredError) as e:
                logger.error(f"Cannot access channel {channel_url}: {e}")
                return []

            except Exception as e:
                logger.error(f"Error parsing channel {channel_url}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(random.uniform(3, 7))
                else:
                    return []

        return []

    def _build_message_link(self, entity, message_id: int) -> str:
        """Безопасное построение ссылки на сообщение"""
        if hasattr(entity, 'username') and entity.username:
            return f"https://t.me/{entity.username}/{message_id}"
        return f"https://t.me/c/{entity.id}/{message_id}"

    def _extract_title(self, text: str, max_length: int = 100) -> str:
        """Извлекает заголовок из текста сообщения"""
        lines = text.split('\n')
        first_line = lines[0].strip()

        if len(first_line) <= max_length:
            return first_line
        return first_line[:max_length - 3] + "..."

    async def validate_channel(self, channel_url: str) -> bool:
        """
        Проверяет, доступен ли канал для парсинга

        Args:
            channel_url: URL или username канала

        Returns:
            True если канал доступен, False иначе
        """
        if not self.client:
            raise RuntimeError("Telegram client not initialized")

        try:
            await self._smart_delay()
            entity = await self.client.get_entity(channel_url)
            return isinstance(entity, (Channel, Chat))
        except Exception as e:
            logger.warning(f"Cannot validate channel {channel_url}: {e}")
            return False

    async def get_channel_info(self, channel_url: str) -> Optional[Dict]:
        """
        Получает информацию о канале

        Args:
            channel_url: URL или username канала

        Returns:
            Словарь с информацией о канале или None
        """
        if not self.client:
            raise RuntimeError("Telegram client not initialized")

        try:
            await self._smart_delay()
            entity = await self.client.get_entity(channel_url)

            return {
                'title': entity.title,
                'username': getattr(entity, 'username', None),
                'id': entity.id,
                'participants_count': getattr(entity, 'participants_count', 0),
                'description': getattr(entity, 'about', ''),
                'is_verified': getattr(entity, 'verified', False),
                'is_broadcast': getattr(entity, 'broadcast', False)
            }
        except Exception as e:
            logger.error(f"Error getting channel info for {channel_url}: {e}")
            return None


# Глобальный экземпляр парсера
_telegram_parser = None


async def get_telegram_parser(api_id: str, api_hash: str, phone_number: str) -> TelegramParser:
    """Получает глобальный экземпляр Telegram парсера"""
    global _telegram_parser
    if _telegram_parser is None:
        _telegram_parser = TelegramParser(api_id, api_hash, phone_number)
    return _telegram_parser


async def parse_telegram_channel(channel_url: str, api_id: str, api_hash: str, phone_number: str, limit: int = 50) -> \
List[Dict]:
    """
    Удобная функция для парсинга одного канала

    Args:
        channel_url: URL канала
        api_id: Telegram API ID
        api_hash: Telegram API Hash
        phone_number: Номер телефона
        limit: Лимит сообщений

    Returns:
        Список сообщений из канала
    """
    async with TelegramParser(api_id, api_hash, phone_number) as parser:
        return await parser.parse_channel(channel_url, limit)


async def validate_telegram_channel(channel_url: str, api_id: str, api_hash: str, phone_number: str) -> bool:
    """
    Удобная функция для валидации канала

    Args:
        channel_url: URL канала
        api_id: Telegram API ID
        api_hash: Telegram API Hash
        phone_number: Номер телефона

    Returns:
        True если канал доступен
    """
    async with TelegramParser(api_id, api_hash, phone_number) as parser:
        return await parser.validate_channel(channel_url)
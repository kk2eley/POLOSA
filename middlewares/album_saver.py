import asyncio
import logging
from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from cachetools import TTLCache

class AlbumsMiddleware(BaseMiddleware):
    def __init__(self, wait_time_seconds: int):
        super().__init__()
        self.wait_time_seconds = wait_time_seconds
        self.albums_cache = TTLCache(
            ttl=float(wait_time_seconds) + 20.0,
            maxsize=1000
        )
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        if event.media_group_id is None:
            return await handler(event, data)

        album_id: str = event.media_group_id

        async with self.lock:
            self.albums_cache.setdefault(album_id, []).append(event)
            self.logger.debug(f"Added message {event.message_id} to cache for album {album_id}")

        await asyncio.sleep(self.wait_time_seconds)

        async with self.lock:
            album_messages = self.albums_cache.pop(album_id, [])
            if not album_messages:
                self.logger.debug(f"No messages found for album {album_id}")
                return

            if album_messages[0].message_id == event.message_id:
                data['album_messages'] = album_messages
                self.logger.debug(f"Album {album_id} with messages {', '.join(str(msg.message_id) for msg in album_messages)} passed to handler")
                return await handler(event, data)
            else:
                self.logger.debug(f"Message {event.message_id} is not the first message in album {album_id}")

# Настройка логирования
# logging.basicConfig(level=logging.DEBUG)

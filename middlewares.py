from aiogram import BaseMiddleware
from aiogram.types import Message
import logging

class LoginMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        logging.info(f"Получено сообщение: {event.text}")
        return await handler(event, data)
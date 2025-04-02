from aiogram.types import TelegramObject
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class DBSessionMiddleware(BaseMiddleware):
    """Мидлварь для создания сессии базы данных"""
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        super().__init__()
        self.session_maker = session_maker

    async def __call__(self, handler, event: TelegramObject, data: dict):
        async with self.session_maker() as session:
            data["session"] = session
            return await handler(event, data)

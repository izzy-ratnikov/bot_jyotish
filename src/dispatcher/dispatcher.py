import logging

from aiogram import Bot, Dispatcher

from src._settings import settings_factory

settings = settings_factory()


logging.basicConfig(level=logging.INFO)


if not settings.API_TOKEN:
    raise ValueError("API_TOKEN not found")

bot = Bot(token=settings.API_TOKEN, request_timeout=settings.REQUEST_TIMEOUT)
dp = Dispatcher()

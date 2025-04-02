import asyncio
import logging
import logging.config
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from utils.logger import logging_config
from keyboards.set_main_menu import set_main_menu
from handlers import form_handlers
# from db.connect import AsyncSessionLocal
# from utils.middlewares import DBSessionMiddleware
from config import settings


logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main() -> None:
    logging.config.dictConfig(logging_config)
    logger.info("Starting BOTV")

    # Инициализируем бот, редис и диспетчер
    bot: Bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    storage = RedisStorage.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )
    dp: Dispatcher = Dispatcher(storage=storage)

    # Настраиваем кнопку Menu бота
    await set_main_menu(bot)

    # Добавляем миддлварь для сессий к БД
    # dp.update.middleware(DBSessionMiddleware(AsyncSessionLocal))

    # Регистриуем роутеры в диспетчере
    dp.include_router(form_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"[Exception] - {e}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

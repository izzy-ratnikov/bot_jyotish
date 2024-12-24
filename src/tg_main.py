import asyncio

import src.commands  # noqa: F401
from src.dispatcher.dispatcher import bot, dp


async def main():
    await dp.start_polling(bot, skip_updates=True)


def run_bot():
    asyncio.run(main())


if __name__ == "__main__":
    run_bot()
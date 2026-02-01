import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import bot.handlers as handlers
from bot.settings import get_settings

settings = get_settings()

if not settings.token:
    raise Exception("Null token provided")


async def main() -> None:
    dp = Dispatcher()

    dp.include_routers(
        handlers.start_router,
        handlers.convert_router,
    )

    bot = Bot(
        token=settings.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

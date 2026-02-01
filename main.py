import asyncio
import logging
import handlers

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from db.backend import init_db
from settings import get_settings

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
    init_db()
    asyncio.run(main())

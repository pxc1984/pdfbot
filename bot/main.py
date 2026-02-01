import asyncio
import logging
from urllib.parse import urlparse

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

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

    if settings.webhook_url:
        parsed = urlparse(settings.webhook_url)
        webhook_path = parsed.path or "/"
        await bot.set_webhook(settings.webhook_url)

        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(
            app, path=webhook_path
        )
        setup_application(app, dp, bot=bot)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host=settings.webhook_host, port=settings.webhook_port)
        await site.start()

        try:
            await asyncio.Event().wait()
        finally:
            await runner.cleanup()
            await bot.session.close()
    else:
        await bot.delete_webhook(drop_pending_updates=False)
        await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

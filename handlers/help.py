from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

help_router = Router()

@help_router.message(Command("help"))
async def help_command(message: Message):
    await message.reply(text="Все оч просто, кидаешь мне пикчу (ОДНУ) и я тебе кидаю в ответ гифку из этой пикчи")

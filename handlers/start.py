from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

start_router = Router()

@start_router.message(CommandStart())
async def start_command(message: Message) -> None:
    await message.answer(text="Бот, который превращает набор изображений в пдф файлик для загрузки в лмску\nВажно: отправляй мне фотки для пдфки как файлы")

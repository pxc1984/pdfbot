import datetime

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from aiogram.enums import ParseMode

from PIL import Image as PILImage
import io

convert_router = Router()

# Храним временно загруженные картинки в памяти (в реальном проекте лучше БД/FS)
user_photos: dict[int, list[tuple[int, PILImage.Image]]] = {}


@convert_router.message(lambda msg: msg.document is not None)
async def convert(message: Message, bot: Bot) -> None:
    global user_photos
    if not message.document:
        await message.answer("кидай фотки (документами), я соберу их в пдфку")
        return

    # Скачиваем файл в память
    file = await bot.get_file(message.document.file_id)
    file_bytes = await bot.download_file(file.file_path)
    image = PILImage.open(file_bytes).convert("RGB")

    # Сохраняем картинку для пользователя
    user_id = message.from_user.id
    if user_id not in user_photos:
        user_photos[user_id] = []
    user_photos[user_id].append((message.message_id, image))

    await message.answer(
        text=(
            f"фото добавлено! сейчас в очереди: {len(user_photos[user_id])}\n"
            "отправь команду /makepdf чтобы собрать пдф\n"
            "отправь команду /cancel чтобы начать сборку с начала"
        ),
        parse_mode=ParseMode.HTML,
    )


@convert_router.message(Command("makepdf"))
async def make_pdf(message: Message, bot: Bot) -> None:
    global user_photos
    user_id = message.from_user.id
    if user_id not in user_photos or not user_photos[user_id]:
        await message.answer("ты мне еще ни одной фотки не скинул")
        return

    images = [img for _, img in sorted(user_photos[user_id], key=lambda x: x[0])]

    # Генерация PDF
    pdf_buffer = io.BytesIO()
    images[0].save(
        pdf_buffer,
        format="PDF",
        save_all=True,
        append_images=images[1:],
    )
    pdf_buffer.seek(0)

    # Отправляем пользователю
    pdf_file = BufferedInputFile(
        pdf_buffer.read(),
        filename=f"{message.from_user.full_name} {datetime.datetime.utcnow()}.pdf",
    )
    await message.answer_document(pdf_file, caption="вот твой пдф")

    # Чистим очередь
    user_photos[user_id].clear()


@convert_router.message(Command("cancel"))
async def cancel_pdf(message: Message, bot: Bot) -> None:
    global user_photos
    user_id = message.from_user.id
    if user_id not in user_photos or not user_photos[user_id]:
        await message.answer(
            "ты мне еще ни одной фотки не скинул, чего я должен чистить то"
        )
        return

    user_photos[user_id].clear()
    await message.answer("все, забыл")

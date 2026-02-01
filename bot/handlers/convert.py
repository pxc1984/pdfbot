import datetime
import io

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from aiogram.enums import ParseMode

from PIL import Image as PILImage

from bot.db import add_photo, list_photo_bytes, delete_photos, count_photos

convert_router = Router()


@convert_router.message(lambda msg: msg.document is not None or msg.photo is not None)
async def convert(message: Message, bot: Bot) -> None:
    if not message.document and not message.photo:
        await message.answer("кидай фотки (документами или обычными), я соберу их в пдфку")
        return

    # Скачиваем файл в память
    if message.photo:
        file_id = message.photo[-1].file_id
    else:
        file_id = message.document.file_id

    file = await bot.get_file(file_id)
    file_bytes = await bot.download_file(file.file_path)
    image_bytes = file_bytes.read()
    try:
        PILImage.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        await message.answer("не смог прочитать картинку, попробуй другой файл")
        return

    # Сохраняем картинку для пользователя
    user_id = message.from_user.id
    total = add_photo(
        chat_id=user_id,
        message_id=message.message_id,
        image_bytes=image_bytes,
    )

    await message.answer(
        text=(
            f"фото добавлено! сейчас в очереди: {total}\n"
            "отправь команду /makepdf чтобы собрать пдф\n"
            "отправь команду /cancel чтобы начать сборку с начала"
        ),
        parse_mode=ParseMode.HTML,
    )


@convert_router.message(Command("makepdf"))
async def make_pdf(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id
    photos = list_photo_bytes(user_id)
    if not photos:
        await message.answer("ты мне еще ни одной фотки не скинул")
        return

    images = [PILImage.open(io.BytesIO(photo)).convert("RGB") for photo in photos]

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
    delete_photos(user_id)


@convert_router.message(Command("cancel"))
async def cancel_pdf(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id
    count = count_photos(user_id)
    if count == 0:
        await message.answer(
            "ты мне еще ни одной фотки не скинул, чего я должен чистить то"
        )
        return

    delete_photos(user_id)
    await message.answer("все, забыл")

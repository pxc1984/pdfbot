import datetime
import io
import re
from pathlib import Path

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.enums import ParseMode

from PIL import Image as PILImage

from bot.db import add_photo, list_photo_paths, delete_photos, count_photos

convert_router = Router()
MEDIA_DIR = Path("/tmp/media")
PDF_DIR = Path("/var/pdf")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)


@convert_router.message(lambda msg: msg.document is not None or msg.photo is not None)
async def convert(message: Message, bot: Bot) -> None:
    if not message.document and not message.photo:
        await message.answer(
            "кидай фотки (документами или обычными), я соберу их в пдфку"
        )
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

    suffix = Path(file.file_path).suffix or ".img"
    image_path = MEDIA_DIR / f"{message.from_user.id}_{message.message_id}{suffix}"
    image_path.write_bytes(image_bytes)

    # Сохраняем картинку для пользователя
    user_id = message.from_user.id
    total = add_photo(
        chat_id=user_id,
        message_id=message.message_id,
        image_path=str(image_path),
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
    photo_paths = list_photo_paths(user_id)
    if not photo_paths:
        await message.answer("ты мне еще ни одной фотки не скинул")
        return

    images = [PILImage.open(path).convert("RGB") for path in photo_paths]

    # Генерация PDF
    raw_name = message.from_user.full_name or str(message.from_user.id)
    safe_name = re.sub(r"[^A-Za-zА-Яа-я0-9 _-]+", "_", raw_name).strip() or str(
        message.from_user.id
    )
    pdf_name = f"{safe_name}_{datetime.datetime.utcnow().date().isoformat()}.pdf"
    pdf_path = PDF_DIR / pdf_name
    images[0].save(
        pdf_path,
        format="PDF",
        save_all=True,
        append_images=images[1:],
    )
    for image in images:
        image.close()

    # Отправляем пользователю
    pdf_file = FSInputFile(path=pdf_path, filename=pdf_name)
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

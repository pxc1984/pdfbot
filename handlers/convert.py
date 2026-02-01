import datetime
import io

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from aiogram.enums import ParseMode

from PIL import Image as PILImage

from db.backend import SessionLocal
from db.models.photo import Photo

convert_router = Router()


@convert_router.message(lambda msg: msg.document is not None)
async def convert(message: Message, bot: Bot) -> None:
    if not message.document:
        await message.answer("кидай фотки (документами), я соберу их в пдфку")
        return

    # Скачиваем файл в память
    file = await bot.get_file(message.document.file_id)
    file_bytes = await bot.download_file(file.file_path)
    image_bytes = file_bytes.read()
    try:
        PILImage.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        await message.answer("не смог прочитать картинку, попробуй другой файл")
        return

    # Сохраняем картинку для пользователя
    user_id = message.from_user.id
    session = SessionLocal()
    try:
        session.add(
            Photo(
                chat_id=user_id,
                message_id=message.message_id,
                image_bytes=image_bytes,
            )
        )
        session.commit()
        total = session.query(Photo).filter_by(chat_id=user_id).count()
    finally:
        session.close()

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
    session = SessionLocal()
    try:
        photos = (
            session.query(Photo)
            .filter_by(chat_id=user_id)
            .order_by(Photo.message_id.asc())
            .all()
        )
        if not photos:
            await message.answer("ты мне еще ни одной фотки не скинул")
            return

        images = [
            PILImage.open(io.BytesIO(photo.image_bytes)).convert("RGB")
            for photo in photos
        ]

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
        session.query(Photo).filter_by(chat_id=user_id).delete()
        session.commit()
    finally:
        session.close()


@convert_router.message(Command("cancel"))
async def cancel_pdf(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id
    session = SessionLocal()
    try:
        count = session.query(Photo).filter_by(chat_id=user_id).count()
        if count == 0:
            await message.answer(
                "ты мне еще ни одной фотки не скинул, чего я должен чистить то"
            )
            return

        session.query(Photo).filter_by(chat_id=user_id).delete()
        session.commit()
        await message.answer("все, забыл")
    finally:
        session.close()

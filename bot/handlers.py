import logging
import os
from aiogram import Router, types, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import ContentType

from bot.utils import process_image, cleanup_file, download_photo, download_document

logger = logging.getLogger(__name__)
router = Router()

@router.message(CommandStart())
async def start_command(message: types.Message):
    """Обработчик команды /start."""
    user_name = message.from_user.first_name or "пользователь"
    await message.answer(f"Привет, {user_name}! 👋\nЯ бот для улучшения качества фотографий. Просто отправь мне картинку, и я постараюсь сделать ее лучше!")

@router.message(Command("help"))
async def help_command(message: types.Message):
    """Обработчик команды /help."""
    help_text = (
        "Я бот для улучшения качества изображений.\n\n"
        "<b>Как пользоваться:</b>\n"
        "1. Просто отправь мне фотографию или изображение как документ.\n"
        "2. Я обработаю его и пришлю улучшенную версию.\n\n"
        "<b>Поддерживаемые форматы:</b> JPG, PNG\n\n"
        "Если у тебя есть вопросы или предложения, свяжись с разработчиком."
    )
    await message.answer(help_text, parse_mode="HTML")

@router.message(F.photo | F.document)
async def process_image_message(message: types.Message, model_session, bot: Bot):
    if message.photo:
        file_path = await download_photo(message.photo[-1], bot)
    elif message.document and message.document.mime_type.startswith('image/'):
        file_path = await download_document(message.document, bot)
    else:
        await message.answer("Пожалуйста, отправьте изображение (фото или документ).")
        return

    if file_path:
        await message.answer("Получил твое изображение, начинаю улучшать качество...")
        enhanced_image_path = await process_image(file_path, model_session)

        if enhanced_image_path:
            try:
                file_size = os.path.getsize(enhanced_image_path)

                if file_size > 10 * 1024 * 1024:  # Лимит размера Telegram (10 MB)
                    await message.answer("Файл слишком большой для отправки в виде фото, отправляю как документ.")
                    with open(enhanced_image_path, 'rb') as file:
                        await message.answer_document(
                            types.BufferedInputFile(file.read(), filename="enhanced_image.png"),
                            caption="Вот улучшенная версия, отправленная как документ!"
                        )
                else:
                    with open(enhanced_image_path, 'rb') as file:
                        await message.answer_photo(
                            types.BufferedInputFile(file.read(), filename="enhanced_image.png"),
                            caption="Вот улучшенная версия!"
                        )
            except Exception as e:
                logger.error(f"Ошибка при отправке файла: {e}")
                await message.answer("Произошла ошибка при отправке улучшенного изображения.")
            finally:
                cleanup_file(enhanced_image_path)
        else:
            await message.answer("Не удалось улучшить качество изображения.")
        cleanup_file(file_path)


@router.message()  # Этот обработчик будет срабатывать на все остальные сообщения
async def unknown_message(message: types.Message):
    await message.answer("Извини, я не понимаю эту команду. Используй /start, чтобы начать, или /help, чтобы узнать больше.")
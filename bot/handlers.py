import logging
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
        "**Как пользоваться:**\n"
        "1. Просто отправь мне фотографию или изображение как документ.\n"
        "2. Я обработаю его и пришлю улучшенную версию.\n\n"
        "**Поддерживаемые форматы:** JPG, PNG и другие распространенные форматы изображений.\n\n"
        "Если у тебя есть вопросы или предложения, свяжись с разработчиком."
    )
    await message.answer(help_text)

@router.message(F.photo | F.document)
async def process_image_message(message: types.Message, model_session, bot: Bot):
    if message.photo:
        file_path = await download_photo(message.photo[-1], bot)  # Передаем экземпляр bot
    elif message.document and message.document.mime_type.startswith('image/'):
        file_path = await download_document(message.document, bot) # Передаем экземпляр bot
    else:
        await message.answer("Пожалуйста, отправьте изображение (фото или документ).")
        return

    if file_path:
        await message.answer("Получил твое изображение, начинаю улучшать качество...")
        enhanced_image_path = await process_image(file_path, model_session)
        if enhanced_image_path:
            with open(enhanced_image_path, 'rb') as photo_file:
                await message.answer_photo(types.BufferedInputFile(photo_file.read(), filename="enhanced_image.png"), caption="Вот улучшенная версия!")
            cleanup_file(enhanced_image_path)
        else:
            await message.answer("Не удалось улучшить качество изображения.")
        cleanup_file(file_path)

@router.message()  # Этот обработчик будет срабатывать на все остальные сообщения
async def unknown_message(message: types.Message):
    await message.answer("Извини, я не понимаю эту команду. Используй /start, чтобы начать, или /help, чтобы узнать больше.")
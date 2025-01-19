import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import ACTIVE_MODEL_PATH, BOT_TOKEN, LOG_FILE, LOG_LEVEL
from bot.handlers import router
from model.inference import load_onnx_model

# Настройка логирования
logging.basicConfig(
    level=LOG_LEVEL,
    filename=LOG_FILE,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    logger.info("Загрузка ONNX модели...")
    model_session = load_onnx_model(ACTIVE_MODEL_PATH)
    if not model_session:
        logger.critical("Не удалось загрузить ONNX модель. Завершение работы.")
        return

    dp.workflow_data["model_session"] = model_session

    dp.include_router(router)

    logger.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")

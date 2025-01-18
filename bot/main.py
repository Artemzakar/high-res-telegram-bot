from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import logging
import asyncio

API_TOKEN = '7846671215:AAHXGXKbGMFSV-lo4pjy8PcHd_mG2klTACE'

# Включение логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я тестовый бот.")

# Команда /help
@dp.message(Command("help"))
async def send_help(message: types.Message):
    await message.reply("Это тестовый бот для команд.\nКоманды:\n/start - Приветствие\n/help - Помощь")

# Команда /test
@dp.message(Command("test"))
async def send_test(message: types.Message):
    await message.reply("Тестовая команда выполнена!")

# Хэндлер для всех сообщений
@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Вы написали: {message.text}")

if __name__ == '__main__':
    # Запуск polling с передачей объекта бота
    asyncio.run(dp.start_polling(bot))

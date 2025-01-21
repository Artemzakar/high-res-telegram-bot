# Используем официальный образ Python 3.9
FROM python:3.9-slim-buster

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код твоего бота
COPY bot ./bot
COPY model ./model

# Указываем команду для запуска бота
CMD ["python", "bot/main.py"]
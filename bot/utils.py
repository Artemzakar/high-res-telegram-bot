import logging
import os
import tempfile

import aiohttp
import onnxruntime as rt
from aiogram import Bot, types
# from PIL import Image

from model.inference import predict_onnx

logger = logging.getLogger(__name__)


async def process_image(
    image_path: str, model_session: rt.InferenceSession
) -> str or None:
    """
    Обрабатывает изображение с использованием ONNX модели.

    Args:
        image_path: Путь к входному изображению.
        model_session: Загруженная сессия ONNX.

    Returns:
        Путь к обработанному изображению или None в случае ошибки.
    """
    try:
        logger.info(f"Начинаю обработку изображения: {image_path}")
        enhanced_image = await predict_onnx(model_session, image_path)
        if enhanced_image:
            # Сохраняем обработанное изображение во временный файл
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                enhanced_image.save(tmp_file.name)
                logger.info(
                    f"Изображение успешно обработано и сохранено: {tmp_file.name}"
                )
                return tmp_file.name
        else:
            logger.error(f"Ошибка при обработке изображения: {image_path}")
            return None
    except Exception as e:
        logger.exception(
            f"Произошла ошибка при обработке изображения {image_path}: {e}"
        )
        return None


def cleanup_file(file_path: str):
    """Удаляет файл по указанному пути."""
    try:
        os.remove(file_path)
        logger.info(f"Файл успешно удален: {file_path}")
    except Exception as e:
        logger.error(f"Ошибка при удалении файла {file_path}: {e}")


async def download_photo(photo: types.PhotoSize, bot: Bot) -> str or None:
    """Скачивает фотографию и возвращает путь к скачанному файлу."""
    try:
        file = await bot.get_file(photo.file_id)
        file_path_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"  # Формируем URL вручную

        temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        async with aiohttp.ClientSession() as session:
            async with session.get(file_path_url) as resp:
                if resp.status == 200:
                    temp_file.write(await resp.read())
                else:
                    logger.error(f"Ошибка при скачивании фото, статус: {resp.status}")
                    return None
        temp_file.close()
        logger.info(f"Файл успешно скачан: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        logger.error(f"Ошибка при скачивании фотографии: {e}")
        return None


async def download_document(document: types.Document, bot: Bot) -> str or None:
    """Скачивает документ и возвращает путь к скачанному файлу."""
    try:
        file = await bot.get_file(document.file_id)
        destination_file = tempfile.gettempdir() + os.sep + document.file_name
        await bot.download_file(file.file_path, destination_file)
        logger.info(f"Файл успешно скачан: {destination_file}")
        return destination_file
    except Exception as e:
        logger.error(f"Ошибка при скачивании документа: {e}")
        return None

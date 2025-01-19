import os
# Путь к директории проекта для корректного импорта config
import sys

import pytest
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from bot import config
from model import inference


@pytest.fixture(scope="module")
def inference_session():
    """Фикстура для загрузки ONNX модели один раз для всех тестов."""
    model_path = config.ACTIVE_MODEL_PATH
    session = inference.load_onnx_model(model_path)
    assert session is not None, f"Не удалось загрузить модель из {model_path}"
    return session


@pytest.fixture
def input_dir():
    """Фикстура для получения пути к директории с входными изображениями."""
    return os.path.join(os.path.dirname(__file__), "test_data", "input")


@pytest.fixture
def output_dir():
    """Фикстура для получения пути к директории для выходных изображений."""
    output_dir_path = os.path.join(os.path.dirname(__file__), "test_data", "output")
    os.makedirs(output_dir_path, exist_ok=True)
    return output_dir_path


def test_inference_on_input_images(inference_session, input_dir, output_dir):
    """Тестирует инференс модели на всех изображениях из входной директории."""
    input_files = sorted(
        [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    )

    for input_file in input_files:
        if not input_file.lower().endswith(
            (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")
        ):
            pytest.skip(f"Пропускаем не поддерживаемый формат файла: {input_file}")
            continue

        input_path = os.path.join(input_dir, input_file)
        output_file = f"output{input_file[len('input'):]}"
        output_path = os.path.join(output_dir, output_file)

        output_image = inference.predict_onnx(inference_session, input_path)
        assert output_image is not None, f"Ошибка при обработке файла: {input_file}"

        if output_image:
            output_image.save(output_path)
            assert os.path.exists(
                output_path
            ), f"Выходной файл не создан: {output_path}"
            try:
                Image.open(output_path).verify()  # Проверка целостности файла
            except Exception as e:
                pytest.fail(f"Выходной файл поврежден: {output_path}. Ошибка: {e}")

import asyncio

import numpy as np
import onnxruntime as rt
from PIL import Image


def load_onnx_model(model_path):
    """Загружает модель ONNX и выбирает провайдера выполнения."""
    try:
        if 'CUDAExecutionProvider' in rt.get_available_providers():
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        else:
            providers = ['CPUExecutionProvider']
        session = rt.InferenceSession(model_path, providers=providers)
        return session
    except RuntimeError as e:
        print(f"Ошибка загрузки модели ONNX: {e}")
        return None


async def predict_onnx(session, image_path):
    """Выполняет предсказание с помощью загруженной модели ONNX асинхронно."""
    try:
        # Функция, которая будет выполняться в отдельном потоке
        def run_inference():
            img = Image.open(image_path).convert("RGB")
            img_np = np.array(img).astype(np.float32) / 255.0
            img_np = img_np.transpose((2, 0, 1))  # CHW

            # Получаем имя входного слоя
            input_name = session.get_inputs()[0].name

            # Расширяем размерность до (1, C, H, W)
            input_image = np.expand_dims(img_np, axis=0)

            output_data = session.run(None, {input_name: input_image})

            output_img = output_data[0][0]

            output_img = output_img.transpose((1, 2, 0))
            output_img = np.clip(output_img * 255.0, 0, 255).astype(np.uint8)
            return Image.fromarray(output_img)

        # Запускаем блокирующую функцию в отдельном потоке
        loop = asyncio.get_running_loop()
        output_image = await loop.run_in_executor(None, run_inference)
        return output_image

    except Exception as e:
        print(f"Ошибка предсказания: {e}")
        return None

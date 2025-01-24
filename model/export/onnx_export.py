import os

import torch

from model.export.RealESRGAN import RealESRGAN


def export_model_to_onnx(weights_path, output_onnx_path, scale):
    """Экспортирует модель RealESRGAN в ONNX формат с динамическими размерами."""
    device = torch.device("cpu")  # Используем CPU для стабильности
    try:
        model = RealESRGAN(device, scale=scale)
        model.load_weights(weights_path)
    except Exception as e:
        print(f"Ошибка загрузки или инициализации модели из {weights_path}: {e}")
        return

    # Вызываем модель для предсказания с dummy_input до экспорта
    dummy_input = torch.randn(1, 3, 256, 256, device=device)
    with torch.no_grad():
        model.model(dummy_input)

    # Экспорт с указанием динамических осей для высоты и ширины
    try:
        torch.onnx.export(
            model.model,
            dummy_input,
            output_onnx_path,
            export_params=True,
            opset_version=12,
            do_constant_folding=True,
            input_names=["input"],
            output_names=["output"],
            dynamic_axes={
                "input": {0: "batch_size", 2: "height", 3: "width"},
                "output": {0: "batch_size", 2: "height", 3: "width"},
            },
        )
        print(f"Модель из {weights_path} успешно экспортирована в {output_onnx_path}")
    except Exception as e:
        print(f"Ошибка экспорта модели из {weights_path}: {e}")


if __name__ == "__main__":
    weights_dir = "weights"
    output_dir = "../versions"

    # Создаем папку versions
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(weights_dir):
        if filename.endswith(".pth"):
            weights_name = filename.replace(".pth", "")
            weights_path = os.path.join(weights_dir, filename)
            output_onnx_name = f"{weights_name}.onnx"
            output_onnx_path = os.path.join(output_dir, output_onnx_name)

            # Определяем scale на основе имени файла
            if "x2" in weights_name:
                scale = 2
            elif "x4" in weights_name:
                scale = 4
            elif "x8" in weights_name:
                scale = 8
            else:
                print(f"Не удалось определить scale для {filename}. Пропускаем.")
                continue

            export_model_to_onnx(weights_path, output_onnx_path, scale)

    print("Экспорт всех моделей завершен.")

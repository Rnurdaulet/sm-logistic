
# services/order_image_service.py
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


class OrderImageService:
    @staticmethod
    def optimize_image(image_field, max_width=1024, max_height=1024, quality=85):
        """
        Оптимизирует изображение: уменьшает размер и сохраняет с заданным качеством.

        Args:
            image_field: Поле изображения из модели (ImageField).
            max_width: Максимальная ширина изображения.
            max_height: Максимальная высота изображения.
            quality: Качество сохранённого изображения (0-100).

        Returns:
            ContentFile: Оптимизированное изображение, готовое для сохранения.
        """
        try:
            # Открываем изображение
            img = Image.open(image_field)
            img = img.convert('RGB')  # Конвертируем в RGB для совместимости

            # Масштабируем изображение пропорционально
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Сохраняем изображение в буфер с оптимизацией
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=quality, optimize=True)
            buffer.seek(0)

            return ContentFile(buffer.read())  # Возвращаем оптимизированный файл
        except Exception as e:
            raise ValueError(f"Ошибка при оптимизации изображения: {e}")

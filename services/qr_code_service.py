# services/qr_code_service.py
import segno
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile

class QRCodeService:
    @staticmethod
    def generate_qr_code(instance, qr_data, text_parts, file_prefix, field_name="qr_code"):
        """
        Генерирует QR-код с дополнительной информацией и сохраняет его в указанное поле модели.

        Args:
            instance: Экземпляр модели, куда сохраняется QR-код.
            qr_data: Строка данных для QR-кода.
            text_parts: Список строк для текста рядом с QR-кодом.
            file_prefix: Префикс имени файла (например, "O" для Order или "W" для Warehouse).
            field_name: Поле модели, куда сохраняется файл QR-кода (по умолчанию "qr_code").
        """
        # Генерация QR-кода
        qr = segno.make(qr_data, micro=False)
        buffer = BytesIO()
        qr.save(buffer, kind="png", scale=5)
        buffer.seek(0)

        # Открываем QR-код как изображение
        qr_image = Image.open(buffer)

        # Настраиваем шрифт
        try:
            font = ImageFont.truetype("arial.ttf", size=20)
        except IOError:
            font = ImageFont.load_default()

        # Определяем ширину и высоту текста
        draw = ImageDraw.Draw(qr_image)
        text_width = max(int(draw.textbbox((0, 0), line, font=font)[2]) for line in text_parts)
        text_height = sum(int(draw.textbbox((0, 0), line, font=font)[3]) for line in text_parts) + (
                len(text_parts) - 1
        ) * 5

        # Создаём новое изображение, добавляя место для текста
        new_width = qr_image.width + text_width + 20
        new_height = max(qr_image.height, text_height)
        new_image = Image.new("RGB", (new_width, new_height), "white")
        new_image.paste(qr_image, (0, 0))

        # Рисуем текст рядом с QR-кодом
        text_x = qr_image.width + 10
        current_y = (new_height - text_height) // 2
        draw = ImageDraw.Draw(new_image)
        for line in text_parts:
            draw.text((text_x, current_y), line, fill="black", font=font)
            current_y += int(draw.textbbox((0, 0), line, font=font)[3]) + 5

        # Сохранение изображения
        buffer = BytesIO()
        new_image.save(buffer, format="PNG")
        buffer.seek(0)

        # Сохранение файла в поле модели
        file_name = f"{file_prefix}_{qr_data}.png"
        getattr(instance, field_name).save(file_name, ContentFile(buffer.getvalue()), save=False)

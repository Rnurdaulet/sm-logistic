from django.db import models
from django.core.exceptions import ValidationError
import re


class Client(models.Model):
    full_name = models.CharField("ФИО", max_length=255)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ['-created_at']  # Сортировка по умолчанию: по дате создания

    def __str__(self):
        phone_list = ", ".join([phone.number for phone in self.phone_numbers.all()])
        return f"{self.full_name} ({phone_list})"

    def get_phone_numbers(self):
        """
        Возвращает все номера телефона клиента через запятую.
        """
        return ", ".join(phone.number for phone in self.phone_numbers.all())

    get_phone_numbers.short_description = "Номера телефонов"  # Описание для админки


class PhoneNumber(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="phone_numbers",
        verbose_name="Клиент"
    )
    number = models.CharField("Номер телефона", max_length=20, unique=True)

    class Meta:
        verbose_name = "Номер телефона"
        verbose_name_plural = "Номера телефонов"
        ordering = ['number']  # Сортировка по номеру телефона

    def __str__(self):
        return self.number

    def clean(self):
        """
        Проверяет, что номер телефона соответствует формату.
        """
        phone_pattern = r'^\+?\d{10,15}$'  # Пример: +77001234567
        if not re.match(phone_pattern, self.number):
            raise ValidationError("Номер телефона должен содержать только цифры и может начинаться с '+'.")
        # Убираем пробелы и дефисы для стандартизации формата
        self.number = re.sub(r"[ \-]", "", self.number)

    def save(self, *args, **kwargs):
        """
        Проверяет номер телефона перед сохранением.
        """
        self.clean()
        super().save(*args, **kwargs)

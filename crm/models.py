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
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.get_phone_numbers()})"

    def get_phone_numbers(self):
        return ", ".join(phone.number for phone in self.phone_numbers.all())

    def get_first_phone_number(self):
        first_phone = self.phone_numbers.first()
        return first_phone.number if first_phone else None


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
        ordering = ['number']

    def __str__(self):
        return self.number

    def clean(self):
        phone_pattern = r'^\+?\d{10,15}$'
        if not re.match(phone_pattern, self.number):
            raise ValidationError("Номер телефона должен содержать только цифры и может начинаться с '+'.")
        self.number = re.sub(r"[ \-]", "", self.number)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

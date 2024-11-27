from django.db import models
from django.core.exceptions import ValidationError
import re

class Client(models.Model):
    full_name = models.CharField("ФИО", max_length=255)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    def __str__(self):
        return self.full_name


class PhoneNumber(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="phone_numbers")
    number = models.CharField("Номер телефона", max_length=20)

    def __str__(self):
        return self.number

    def clean(self):
        phone_pattern = r'^\+?\d{10,15}$'  # Пример: +77001234567
        if not re.match(phone_pattern, self.number):
            raise ValidationError("Номер телефона должен содержать только цифры и может начинаться с '+'.")

from django.db import models

class DummyModel(models.Model):
    """
    Фиктивная модель для добавления кастомной страницы в админку.
    """
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Фиктивная модель"
        verbose_name_plural = "Фиктивные модели"

    def __str__(self):
        return self.name or "Фиктивный объект"


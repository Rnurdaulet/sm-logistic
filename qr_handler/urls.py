from django.urls import path
from qr_handler import views

urlpatterns = [
    path('', views.index, name='home'),  # Маршрут для главной страницы
]

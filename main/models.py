from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone


class User(AbstractUser):
    client_flag = models.BooleanField(default=False)


class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_pic_url = models.URLField(verbose_name='Ссылка на изображение профиля', null=True, blank=True)


class Message(models.Model):
    message_text = models.TextField(verbose_name='Текст сообщения')
    receive_date = models.DateField(verbose_name='Дата получения сообщения', default=timezone.now().date())
    receive_time = models.TimeField(verbose_name='Время получения сообщения', default=timezone.now().time())
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Привязка к кленту')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Отправитель')

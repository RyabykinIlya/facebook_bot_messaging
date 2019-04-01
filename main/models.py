from django.db import models
from django.contrib.auth.models import User, AbstractUser

class User(AbstractUser):
    client_flag = models.BooleanField(default=False)


class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_pic_url = models.URLField(verbose_name='Ссылка на изображение профиля', null=True, blank=True)


class Message(models.Model):
    message_text = models.TextField(verbose_name='Текст сообщения')
    receive_date = models.DateField(verbose_name='Дата получения сообщения', auto_now_add=True, blank=True)
    receive_time = models.TimeField(verbose_name='Время получения сообщения', auto_now_add=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Привязка к кленту')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Отправитель')

    class Meta:
        ordering = ['receive_date', 'receive_time']
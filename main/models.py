from django.db import models

# Create your models here.


class Client(models.Model):
    name = models.CharField(max_length=15, verbose_name='Ник')

class Message(models.Model):
    message_text = models.TextField(verbose_name='Текст сообщения')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
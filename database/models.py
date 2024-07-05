from datetime import datetime

from tortoise.models import Model
from tortoise import fields


class Queue(Model):
    # представлення моделі черги в бд для парсингу
    id = fields.IntField(primary_key=True)
    chat_url = fields.CharField(max_length=250)
    status = fields.CharField(max_length=80, null=True, default="in_order")
    bot = fields.ForeignKeyField('models.Bot', related_name='bot', null=True)
    client = fields.ForeignKeyField('models.Client', related_name='client')

    def __str__(self):
        return self.chat_url


class Bot(Model):
    # представлення бота
    id = fields.IntField(primary_key=True)
    token = fields.CharField(max_length=500)
    is_busy = fields.BooleanField(default=False)

    def __str__(self):
        return str(self.token)


class Client(Model):
    # представлення клієнта сервісу
    id = fields.IntField(primary_key=True, auto_increment=False)
    fullname = fields.CharField(max_length=250)
    username = fields.CharField(max_length=250, null=True)
    register_date = fields.DateField(default=datetime.now)

    def __str__(self):
        return str(self.id)


class Chat(Model):
    id = fields.IntField(primary_key=True, auto_increment=False)
    title = fields.CharField(max_length=250)
    link = fields.CharField(max_length=250, null=True)

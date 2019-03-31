from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from main.models import Client, Message
from main.models import User

admin.site.register(Client)
admin.site.register(Message)


admin.site.register(User, UserAdmin)
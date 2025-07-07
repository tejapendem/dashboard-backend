from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


# admin.site.register(Team)

class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ['id', 'username', 'email', 'is_staff']

admin.site.register(CustomUser, CustomUserAdmin)
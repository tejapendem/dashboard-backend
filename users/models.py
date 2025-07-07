# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# from django.contrib.auth import get_user_model
# User = get_user_model()


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    

class Team(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# class CustomUser(AbstractUser):
#     # Add extra fields if needed
#     pass


# class Team(models.Model):
#     name = models.CharField(max_length=100)
#     members = models.ManyToManyField(CustomUser, related_name='teams')

#     def __str__(self):
#         return self.name

# class Team(models.Model):
#     name = models.CharField(max_length=100)
#     members = models.ManyToManyField(User, related_name="teams")
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name


# class Team(models.Model):
#     name = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name
    


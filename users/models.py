from django.contrib.auth.models import AbstractUser
from django.db import models


class BookUser(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    picture = models.ImageField(upload_to='media/profile', blank=True, null=True)
    phone_number = models.CharField(max_length=11)
    telegram_id = models.CharField(max_length=35, unique=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

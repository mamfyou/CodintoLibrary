from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


# from books.models import Book


class BookUser(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    picture = models.ImageField(upload_to='media/profile', blank=True, null=True)
    phone_number = models.CharField(max_length=11, unique=True)
    telegram_id = models.CharField(max_length=35, unique=True)
    email = models.CharField(max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Bookshelf(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(BookUser, on_delete=models.CASCADE, related_name='bookshelf')
    book = models.ManyToManyField("books.Book", related_name='bookBookshelf')
    created_at = models.DateTimeField(auto_now_add=True)




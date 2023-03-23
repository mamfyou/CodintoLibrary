from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


# from books.models import Book


class BookUser(AbstractUser):
    first_name = models.CharField(max_length=255, verbose_name='نام')
    last_name = models.CharField(max_length=255, verbose_name='نام خانوادگی')
    picture = models.ImageField(upload_to='media/profile', blank=True, null=True, verbose_name='تصویر پروفایل')
    phone_number = models.CharField(max_length=11, unique=True, verbose_name='شماره تلفن')
    telegram_id = models.CharField(max_length=35, unique=True, verbose_name='آیدی تلگرام')
    email = models.CharField(max_length=60, unique=True, verbose_name='ایمیل')
    username = models.CharField(max_length=30, unique=True, verbose_name='نام کاربری')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Bookshelf(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(BookUser, on_delete=models.CASCADE, related_name='userBookshelf', verbose_name='کاربر')
    book = models.ManyToManyField("books.Book", related_name='bookBookshelf', verbose_name='کتاب')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')




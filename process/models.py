from django.contrib.auth import get_user_model
from django.db import models

from books.models import Book


class History(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='userHistory', verbose_name='کاربر')
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE, related_name='bookHistory', verbose_name='کتاب')
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    start_date = models.DateField(verbose_name='تاریخ شروع')
    end_date = models.DateField(verbose_name='تاریخ پایان')
    is_extended = models.BooleanField(default=False, verbose_name='تمدید شده')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_accepted = models.BooleanField(default=False, verbose_name='تایید شده')

    def __str__(self):
        return f'{self.book.name}' + '->' + f'{self.user.name}'


class Notification(models.Model):
    TYPE_CHOICES = (
        ('BR', 'Borrow'),
        ('RT', 'Return'),
        ('EX', 'Extend'),
        ('TW', 'Time Warning'),
        ('GN', 'General'),
        ('AV', 'Available'),
        ('CM', 'Comment'),
    )
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default='GN', verbose_name='نوع')
    title = models.CharField(max_length=50, verbose_name='عنوان')
    description = models.TextField(max_length=500, verbose_name='توضیحات')
    user = models.ForeignKey(get_user_model(), related_name='userNotification', on_delete=models.CASCADE, verbose_name='کاربر')
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    picture = models.ImageField(upload_to='media/notifications', verbose_name='عکس')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')


class Request(models.Model):
    TYPE_CHOICES = (
        ('BR', 'امانت'),
        ('RT', 'بازگشت'),
        ('EX', 'تمدید'),
        ('CM', 'کامنت'),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='requestUser', verbose_name='کاربر')
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE, related_name='requestBook', verbose_name='کتاب')
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, verbose_name='نوع')
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    metadata = models.JSONField(null=True, blank=True, default=None, verbose_name='متادیتا')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    is_accepted = models.BooleanField(default=None, null=True, blank=True, verbose_name='تایید شده')


class AvailableNotification(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='availableNotifUser', verbose_name='کاربر')
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE, related_name='availableNotifBook', verbose_name='کتاب')

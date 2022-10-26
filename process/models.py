from django.contrib.auth import get_user_model
from django.db import models


class History(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='userHistory')
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE, related_name='bookHistory')
    created = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_extended = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)

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
    )
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default='GN')
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    user = models.ForeignKey(get_user_model(), related_name='userNotification', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True, default=None)
    is_read = models.BooleanField(default=False)


class Request(models.Model):
    TYPE_CHOICES = (
        ('BR', 'امانت'),
        ('RT', 'بازگشت'),
        ('EX', 'تمدید'),
        ('CM', 'کامنت')
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='requestUser')
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE, related_name='requestBook')
    text = models.TextField()
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField()
    is_accepted = models.BooleanField(default=None, null=True)


class AvailableNotification(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='availableNotifUser')
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE, related_name='availableNotifBook')

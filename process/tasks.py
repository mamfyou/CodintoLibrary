import datetime

from celery import shared_task
from django.contrib.auth import get_user_model

from books.models import Book
from process.models import Notification, AvailableNotification, History


@shared_task
def make_notifications_for_available_book(book_id):
    book = Book.objects.get(id=book_id)
    for i in AvailableNotification.objects.filter(book=book):
        Notification.objects.create(user=i.user, type='GN', title='موجود شد!',
                                    description=f'هم اکنون موجود شد!' + f'{book.name}' + f'کتاب',
                                    metadata={'book': book.id})


@shared_task
def make_new_book_notification(book_id):
    book = Book.objects.get(id=book_id)
    for i in get_user_model().objects.all():
        Notification.objects.create(user=i, type='GN', title='کتاب جدید!',
                                    description=f'به کتابخانه کدینتو اضافه شد🥳' + f'{book.name}' + f'کتاب',
                                    metadata={'book': book.id})


@shared_task
def erase_notifications():
    expired_notifications = Notification.objects.filter(
        created__lt=datetime.datetime.now() - datetime.timedelta(days=7))
    expired_notifications.delete()


@shared_task
def time_warning_notification():
    history = History.objects.filter(is_active=True, is_accepted=True)

    for i in history:
        days_left = (i.end_date - datetime.datetime.now()).days
        if days_left <= 3:
            Notification.objects.create(title='هشدار زمان تحویل کتاب', type='GN', user=i.user,
                                        metadata={"book": i.book.id},
                                        description=f'فرصت باقی است😥' + f'{days_left}' + f'تنها' + f'{i.book.name}' + f'برای تحویل کتاب')

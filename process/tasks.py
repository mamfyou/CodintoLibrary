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
                                    picture=book.thumbnail)


@shared_task
def make_new_book_notification(book_id):
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        print(f"Error: Book with id={book_id} does not exist.")
        return
    for i in get_user_model().objects.all():
        Notification.objects.create(user=i, type='GN', title='کتاب جدید!', picture=book.thumbnail,
                                    description=(f'به کتابخانه کدینتو اضافه شد🥳' + f'{book.name}' + f'کتاب '),
                                    )


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
                                        picture=i.book.thumbnail,
                                        description=f'فرصت باقی است😥' + f'{days_left}' + f'تنها' + f'{i.book.name}' + f'برای تحویل کتاب')


@shared_task
def make_new_general_notification_for_every_one(title, description, picture):
    for i in get_user_model().objects.all():
        Notification.objects.create(title=title, description=description, type='GN', user=i, picture=picture)

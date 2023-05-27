from django.contrib.auth import get_user_model
from django.dispatch import receiver

from books.models import Book
from process.models import Notification
from process.signals import available_book, new_general_notif
from process.tasks import make_notifications_for_available_book, make_new_general_notification_for_every_one


@receiver(available_book)
def make_notification(sender, **kwargs):
    make_notifications_for_available_book.delay(picture=kwargs['picture'])


@receiver(new_general_notif)
def make_general_notification(sender, **kwargs):
    # book = Book.objects.get(id=kwargs['book'])
    for i in get_user_model().objects.all():
        # print(picture)
        Notification.objects.create(title=kwargs['title'], description=kwargs['description'], type='GN', user=i, picture=kwargs['picture'])
    # make_new_general_notification_for_every_one.delay(title=kwargs['title'], description=kwargs['description'],
    #                                                   picture=kwargs['picture'])

from django.dispatch import receiver
from process.signals import available_book, new_general_notif
from process.tasks import make_notifications_for_available_book, make_new_general_notifiction_for_every_one


@receiver(available_book)
def make_notification(sender, **kwargs):
    make_notifications_for_available_book.delay(book_id=kwargs['book_id'])


@receiver(new_general_notif)
def make_general_notification(sender, **kwargs):
    make_new_general_notifiction_for_every_one.delay(title=kwargs['title'], description=kwargs['description'],
                                                     metadata=kwargs['metadata'].get('book'))

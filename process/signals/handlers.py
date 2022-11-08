from django.dispatch import receiver
from process.signals import available_book
from process.tasks import make_notifications_for_available_book


@receiver(available_book)
def make_notification(sender, **kwargs):
    make_notifications_for_available_book.delay(book_id=kwargs['book_id'])
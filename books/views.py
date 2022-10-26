from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from books.models import Book
from .serializer import *


class BookMainPage(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Book.objects.select_related('owner').all()

    def get_serializer_context(self):
        return {'user': self.request.user, 'book_id': self.kwargs.get('pk'), 'request': self.request}

    def get_serializer_class(self):
        if self.kwargs.get('pk') is None:
            return MainPageSerializer
        return BookComplexSerializer

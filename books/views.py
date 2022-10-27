from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from .serializer import *


class BookMainPage(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Book.objects.select_related('owner').all()

    def get_serializer_context(self):
        return {'user': self.request.user, 'book_id': self.kwargs.get('pk'), 'request': self.request}

    def get_serializer_class(self):
        if self.kwargs.get('pk') is None:
            return MainPageSerializer
        return BookComplexSerializer


class BorrowBook(ListModelMixin, CreateModelMixin, GenericViewSet):
    def get_queryset(self):
        queryset = Book.objects.filter(id=self.kwargs['book_pk'])
        if queryset.exists():
            return queryset
        return None

    def get_serializer_context(self):
        return {'user': self.request.user, 'book_id': self.kwargs.get('book_pk'), 'request': self.request}

    serializer_class = BookBorrowSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'درخواست شما با موفقیت ثبت شد😍'}, status=status.HTTP_201_CREATED, headers=headers)


class ExtendBook(ListModelMixin, CreateModelMixin, GenericViewSet):
    def get_queryset(self):
        queryset = Book.objects.filter(id=self.kwargs['book_pk'])
        if queryset.exists():
            return queryset
        return None

    def get_serializer_context(self):
        return {'user': self.request.user, 'book_id': self.kwargs.get('book_pk'), 'request': self.request}

    serializer_class = BookExtendSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'درخواست شما با موفقیت ثبت شد😍'}, status=status.HTTP_201_CREATED, headers=headers)


class ReturnBook(ListModelMixin, CreateModelMixin, GenericViewSet):
    def get_queryset(self):
        queryset = Book.objects.filter(id=self.kwargs['book_pk'])
        if queryset.exists():
            return queryset
        return None

    def get_serializer_context(self):
        return {'user': self.request.user, 'book_id': self.kwargs.get('book_pk'), 'request': self.request}

    serializer_class = BookReturnSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'درخواست شما با موفقیت ثبت شد😍'}, status=status.HTTP_201_CREATED, headers=headers)

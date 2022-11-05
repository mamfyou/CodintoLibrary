from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
from .serializer import *
from .Filter import *


class BookMainPage(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Book.objects.select_related('owner').all()[0:1]

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


class CommentBook(ListModelMixin, CreateModelMixin, GenericViewSet, UpdateModelMixin):
    lookup_field = 'pk'

    def get_queryset(self):
        comment_queryset = Comment.objects.filter(book_id=self.kwargs['book_pk'])
        if self.kwargs.get('pk') is not None:
            return comment_queryset
        return comment_queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.kwargs.get('pk') is None:
            return BookCommentSerializer
        return CommentFeedbackSerializer

    def get_serializer_context(self):
        return {'user': self.request.user, 'book_id': self.kwargs.get('book_pk'), 'request': self.request,
                'comment': self.kwargs.get('pk')}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'درخواست شما با موفقیت ثبت شد! برای پاسخ ادمین منتظر باشید 🙏'},
                        status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        if queryset is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)


class BookSearch(ListAPIView):
    serializer_class = BookSearchSerializer
    filterset_class = BookFilter

    def get_queryset(self):
        query_params = self.request.query_params
        if query_params is not None:
            return Book.objects.all()
        return None

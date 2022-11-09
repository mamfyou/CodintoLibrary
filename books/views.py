from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
from .serializer import *
from .Filter import *


class BookMainPage(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    def get_queryset(self):
        if self.kwargs.get('pk') is None:
            return Book.objects.select_related('owner').all()[0:1]
        return Book.objects.select_related('owner').all()

    def get_serializer_context(self):
        return {'user': self.request.user, 'book_id': self.kwargs.get('pk'), 'request': self.request}

    def get_serializer_class(self):
        if self.kwargs.get('pk') is None:
            return MainPageSerializer
        return BookComplexSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class BorrowBook(ListModelMixin, CreateModelMixin, GenericViewSet):
    def get_queryset(self):
        return Book.objects.filter(id=self.kwargs['book_pk'])

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
    search_fields = ['name']

    def get_queryset(self):
        if self.request.query_params is not None:
            return Book.objects.all()
        return None

    def list(self, request, *args, **kwargs):
        if ((self.request.query_params.get('new') == 'true')
            and (self.request.query_params.get('most_popular') == 'true' or self.request.query_params.get(
                    'most_wanted') == 'true')) or \
                ((self.request.query_params.get('most_wanted') == 'true')
                 and (self.request.query_params.get('new') == 'true' or self.request.query_params.get(
                            'most_popular') == 'true')) or \
                ((self.request.query_params.get('most_popular') == 'true')
                 and (self.request.query_params.get('most_wanted') == 'true' or self.request.query_params.get(
                            'new') == 'true')):
            return Response(data={'message': 'نمیتوانید همزمان بیش از یک پارامتر را برای مرتب سازی انتخاب کنید'},
                            status=status.HTTP_400_BAD_REQUEST)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AvailableNotif(CreateAPIView):
    serializer_class = AvailableNotifSerializer
    queryset = Book.objects.all()

    def get_serializer_context(self):
        return {'user': self.request.user, 'request': self.request, 'book_id': self.kwargs.get('pk')}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if AvailableNotification.objects.filter(user=request.user, book=self.kwargs.get('pk')).exists():
            return Response({'message': 'اعلان تنظیم شد!'}, status=status.HTTP_201_CREATED, headers=headers)
        return Response({'message': 'اعلان حذف شد!'}, status=status.HTTP_204_NO_CONTENT, headers=headers)

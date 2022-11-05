from django.contrib.auth import get_user_model
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework.mixins import UpdateModelMixin, ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from .Filter import *

from .serializer import *


# Create your views here.
class CreateUser(CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = CreateUserSerializer


class RequestViewset(GenericViewSet, ListModelMixin, UpdateModelMixin):
    lookup_field = 'pk'

    def get_queryset(self):
        return Request.objects.all().select_related('book').order_by('-created')

    serializer_class = RequestSerializer
    filterset_class = RequestFilter

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(data={'message': 'Successful'})


class BookViewset(GenericViewSet, ListModelMixin, CreateModelMixin, UpdateModelMixin, RetrieveModelMixin):
    lookup_field = 'pk'

    def get_queryset(self):
        return Book.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET' and self.kwargs.get('pk') is None:
            return BookListSerializer
        return BookSerializer

    search_fields = ['name']
    filterset_fields = ['category']


class Category(ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = BookCategory.objects.all()


class NotificationViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
    def get_queryset(self):
        return Notification.objects.all()



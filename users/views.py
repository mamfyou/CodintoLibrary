from rest_framework import status
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, CreateModelMixin, DestroyModelMixin, \
    RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from process.models import Request
from .models import Bookshelf
from .Filter import *
from .serializer import *
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView, ListAPIView
from books.models import Book


# Create your views here.

class MainPanel(ListAPIView):
    lookup_field = 'pk'

    def get_queryset(self):
        return get_user_model().objects.filter(id=self.request.user.id)

    serializer_class = PanelMainPageSerializer


class PanelProfile(RetrieveUpdateAPIView):
    def get_object(self):
        return get_user_model().objects.get(id=self.request.user.id)

    serializer_class = PanelProfileSerializer


class PanelBook(ListAPIView):
    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user).order_by('-created_at')

    def get_serializer_context(self):
        return {'user': self.request.user, 'request': self.request}

    serializer_class = PanelBookSerializer


class PanelCommentViewSet(ListModelMixin, GenericViewSet, DestroyModelMixin):
    lookup_field = 'pk'

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

    serializer_class = CommentPanelSerializer
    filterset_class = CommentPanelFilter

    def get_serializer_context(self):
        return {'user': self.request.user, 'request': self.request}

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT, data={'message': 'comment deleted'})


class PanelNotificationViewSet(GenericViewSet, ListModelMixin, UpdateModelMixin):
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    serializer_class = PanelNotificationSerializer
    filterset_class = NotificationPanel


class PanelBookshelfViewSet(ModelViewSet):
    lookup_field = 'pk'
    def get_queryset(self):
        return Bookshelf.objects.filter(user=self.request.user)

    serializer_class = PanelBookshelfSerializer

    def get_serializer_context(self):
        return {'user': self.request.user, 'request': self.request}

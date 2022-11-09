from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .Filter import *
from .serializer import *


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


class PanelCommentViewSet(ListModelMixin, GenericViewSet, DestroyModelMixin, UpdateModelMixin):
    lookup_field = 'pk'

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user).select_related('book')

    serializer_class = CommentPanelSerializer
    filterset_class = CommentPanelFilter

    def get_serializer_context(self):
        return {'user': self.request.user, 'request': self.request}

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT, data={'message': 'comment deleted'})

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

        return Response(data={'message': 'درخواست شما با موفقیت ثبت شد! برای پاسخ ادمین منتظر باشید 😍'})


class PanelNotificationViewSet(GenericViewSet, ListModelMixin, UpdateModelMixin):
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created')

    serializer_class = PanelNotificationSerializer
    filterset_class = NotificationPanel


class PanelBookshelfViewSet(ModelViewSet):
    lookup_field = 'pk'

    def get_queryset(self):
        return Bookshelf.objects.filter(user=self.request.user).prefetch_related('book')

    serializer_class = PanelBookshelfSerializer

    def get_serializer_context(self):
        return {'user': self.request.user, 'request': self.request}
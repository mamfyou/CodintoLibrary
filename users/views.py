from django.db.models import Q
from rest_framework import status
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, CreateModelMixin, DestroyModelMixin, \
    RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from process.models import Request
from .models import Bookshelf
from .Filter import *
from .serializer import *
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView, ListAPIView, CreateAPIView
from books.models import Book
from rest_framework_simplejwt.tokens import RefreshToken, BlacklistMixin


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
        return Comment.objects.filter(user=self.request.user)

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
        return Bookshelf.objects.filter(user=self.request.user)

    serializer_class = PanelBookshelfSerializer

    def get_serializer_context(self):
        return {'user': self.request.user, 'request': self.request}


class BlacklistRefreshView(APIView, BlacklistMixin):
    def post(self, request):
        try:
            refresh_token = request.data['token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

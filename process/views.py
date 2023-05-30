from django.db.models import Max
from rest_framework import status
from rest_framework.mixins import UpdateModelMixin, ListModelMixin, RetrieveModelMixin, CreateModelMixin, \
    DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet

from .Filter import NotificationFilter, HistoryFilter, RequestFilter
from .permissoins import *
from .serializer import *
from .tasks import make_new_book_notification


# Create your views here.
class UserViewSet(ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [IsSuperUser]
    search_fields = ['username', 'first_name', 'last_name']

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        if instance.is_superuser:
            return Response(data={'message': 'شما نمیتوانید مدیر کتابخانه را حذف کنید!'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RequestViewset(GenericViewSet, ListModelMixin, UpdateModelMixin):
    lookup_field = 'pk'

    def get_queryset(self):
        return Request.objects.all().select_related('book').order_by('-created')

    serializer_class = RequestSerializer
    filterset_class = RequestFilter
    permission_classes = [IsSuperUser]

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


class BookViewset(ModelViewSet):
    lookup_field = 'pk'

    def get_queryset(self):
        max_indent = BookCategory.objects.all().aggregate(Max('indent'))['indent__max']
        if max_indent is None:
            max_indent = 0
        return Book.objects.select_related('owner').prefetch_related(
            'category' + '__parent' * max_indent).all().order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'GET' and self.kwargs.get('pk') is None:
            return BookListSerializer
        return BookSerializer

    search_fields = ['name']
    filterset_fields = ['category']
    permission_classes = [IsSuperUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = serializer.save()
        headers = self.get_success_headers(serializer.data)
        make_new_book_notification.delay(book_id=book.id)
        return Response({'message': 'با موفقیت اضافه شد!'}, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'با موفقیت حذف شد!'}, status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ReadOnlyModelViewSet, CreateModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = CategorySerializer
    queryset = BookCategory.objects.all()
    def get_queryset(self):
        if self.request.query_params:
            return BookCategory.objects.all()
        return BookCategory.objects.filter(parent__isnull=True)

    permission_classes = [IsSuperUser]
    filterset_fields = ['parent']


class NotificationViewSet(GenericViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin):
    def get_queryset(self):
        return Notification.objects.filter(type='GN', user=self.request.user).order_by('-created')

    serializer_class = NotificationSerializer
    filterset_class = NotificationFilter
    permission_classes = [IsSuperUser]


class HistoryViewSet(ListModelMixin, GenericViewSet):
    def get_queryset(self):
        return History.objects.filter(is_active=False, is_accepted=True).order_by('-created')

    serializer_class = HistorySerializer
    permission_classes = [IsSuperUser]
    filterset_class = HistoryFilter

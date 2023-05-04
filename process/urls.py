from django.urls import path, include
from rest_framework_nested.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register('adminpanel/requests', RequestViewset, basename='requests')
router.register('adminpanel/books', BookViewset, basename='books')
router.register('adminpanel/notifications', NotificationViewSet, basename='notifications')
router.register('adminpanel/user', UserViewSet, basename='user')
router.register(('adminpanel/category'), CategoryViewSet, basename='category')
router.register(('adminpanel/history'), HistoryViewSet, basename='history')

urlpatterns = [
    path('', include(router.urls)),
    # path('adminpanel/createuser/', CreateUser.as_view(), name='admin-create_user'),
]

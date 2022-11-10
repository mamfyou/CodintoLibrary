from django.urls import path, include
from .views import *
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

router = DefaultRouter()
router.register('adminpanel/requests', RequestViewset, basename='requests')
router.register('adminpanel/books', BookViewset, basename='books')
router.register('adminpanel/notifications', NotificationViewSet, basename='notifications')
router.register('adminpanel/user', UserViewSet, basename='user')
router.register(('adminpanel/category'), Category, basename='category')
urlpatterns = [
    path('', include(router.urls)),
    # path('adminpanel/createuser/', CreateUser.as_view(), name='admin-create_user'),
]

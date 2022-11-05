from django.urls import path, include
from .views import *
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

router = DefaultRouter()
router.register('adminpanel/requests', RequestViewset, basename='requests')
router.register('adminpanel/books', BookViewset, basename='books')
router.register('adminpanel/notifications', BookViewset, basename='notifications')

urlpatterns = [
    path('', include(router.urls)),
    path('adminpanel/createuser/', CreateUser.as_view(), name='admin-create_user'),
    path('adminpanel/category/', Category.as_view(), name='category')
]

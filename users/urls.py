from django.urls import path, include
from .views import *
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

#
router = DefaultRouter()
router.register(r'panel/bookshelf', PanelBookshelfViewSet, basename='panel-bookshelf')
router.register(r'panel/notification', PanelNotificationViewSet, basename='panel-notification')
router.register(r'panel/comments', PanelCommentViewSet, basename='panel-comment')

urlpatterns = [
    path('', include(router.urls)),
    path('panel/', MainPanel.as_view(), name='panel-main-page'),
    path('panel/profile/', PanelProfile.as_view(), name='panel-profile'),
    path('panel/books/', PanelBook.as_view(), name='panel-books'),
]

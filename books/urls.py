from django.urls import path, include
from rest_framework_nested.routers import NestedSimpleRouter, DefaultRouter
from .views import *

router = DefaultRouter()
router.register('book', BookMainPage, basename='book')

nested_router = NestedSimpleRouter(router, 'book', lookup='book')
nested_router.register('comment', CommentBook, basename='comment-book')
nested_router.register('borrow', BorrowBook, basename='borrow-book')
nested_router.register('extend', ExtendBook, basename='extend-book')
nested_router.register('return', ReturnBook, basename='return-book')


urlpatterns = [
    path('booksearch/', BookSearch.as_view(), name='book-search'),
    path('book/<int:pk>/available/', AvailableNotif.as_view(), name='available-notif'),
    path('', include(router.urls)),
    path('', include(nested_router.urls)),
]

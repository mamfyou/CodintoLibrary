from django.urls import path, include
from rest_framework_nested.routers import NestedSimpleRouter, DefaultRouter
from .views import *

router = DefaultRouter()
router.register('book', BookMainPage)

borrow_router = NestedSimpleRouter(router, 'book', lookup='book')
# borrow_router.register('comment', CommentBook, basename='comment-book')
borrow_router.register('borrow', BorrowBook, basename='borrow-book')
borrow_router.register('extend', ExtendBook, basename='extend-book')
borrow_router.register('return', ReturnBook, basename='return-book')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(borrow_router.urls)),
]

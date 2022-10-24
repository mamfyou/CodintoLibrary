from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('book', BookMainPage)

urlpatterns = [
    path('', include(router.urls))
]

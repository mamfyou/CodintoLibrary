from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register('book', BookMainPage)

urlpatterns = [
    path('', include(router.urls))
]

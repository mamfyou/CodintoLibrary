from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
      path('', include('books.urls')),
      path('', include('users.urls')),
      path('', include('process.urls')),
      path('auth/login/', login_view),
      path('auth/logout/', logout_view),
      path('admin/', admin.site.urls),
      path('debug/', include('debug_toolbar.urls')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +\
              static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
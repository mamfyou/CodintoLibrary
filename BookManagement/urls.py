from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
      path('', include('books.urls')),
      path('', include('users.urls')),
      path('', include('process.urls')),
      path('auth/', include('rest_framework.urls')),
      path('admin/', admin.site.urls),
      path('debug/', include('debug_toolbar.urls')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +\
              static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
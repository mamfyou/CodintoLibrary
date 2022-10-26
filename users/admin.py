from django.contrib import admin
from .models import BookUser


# Register your models here.
@admin.register(BookUser)
class BookUserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email', 'phone_number', 'telegram_id')
    list_per_page = 25

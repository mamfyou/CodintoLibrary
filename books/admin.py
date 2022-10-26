from django.contrib import admin
from .models import BookCategory, Book


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'description']
    list_per_page = 20


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'owner', 'publisher', 'publish_date', 'volume_num', 'page_count', 'translator',
                    'get_category', 'description']
    list_per_page = 20

    def get_category(self, obj):
        return obj.category.name

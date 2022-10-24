from rest_framework import serializers
from books.models import Book


class MainPageSerializer(serializers.Serializer):
    @staticmethod
    def get_new_books(self):
        return Book.objects.all().order_by('-created_at')[:10]

    @staticmethod
    def get_popular_books(self):
        return Book.objects.all().order_by('-bookRate')[:10]

    @staticmethod
    def get_most_borrowed(self):
        return Book.objects.all().order_by('-wanted_to_read')[:10]

    new_books = serializers.SerializerMethodField(method_name='get_new_books')
    popular_books = serializers.SerializerMethodField(method_name='get_popular_books')
    most_borrowed_books = serializers.SerializerMethodField(method_name='get_most_borrowed')


class BookComplexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'picture', 'name', 'author', 'owner', 'publisher', 'publish_date', 'volume_num', 'page_count',
                  'translator', 'category', 'descriptions', 'bookComment']

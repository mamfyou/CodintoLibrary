import os
from datetime import datetime, date

from rest_framework import serializers
from books.models import Book, BookCategory, Comment, Rate
from process.models import AvailableNotification, History, Request


class RateSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ['rate']


class BookSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'picture']

    def get_picture(self, obj: Book):
        request = self.context['request']
        photo_url = obj.picture.url
        return request.build_absolute_uri(photo_url)

    picture = serializers.SerializerMethodField(method_name='get_picture')


class CategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCategory
        fields = ['id', 'name']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'like_count', 'dislike_count', 'rate']

    def get_rate(self, obj):
        rate_object = Rate.objects.filter(user=self.context['user'], book_id=self.context['book_id'])
        if rate_object.exists():
            return rate_object.first().rate
        return None

    rate = serializers.SerializerMethodField(method_name='get_rate')


class BookComplexSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()

    class Meta:
        model = Book
        fields = ['id', 'picture', 'name', 'author', 'owner', 'publisher', 'publish_date', 'volume_num', 'page_count',
                  'translator', 'category', 'description', 'bookComment', 'is_available', 'has_available_notif',
                  'has_borrowed', 'deadline', 'has_sent_request']

    def get_category(self, obj: Book):
        cat_holder = []
        for cat in obj.category.all():
            cat_holder.append(cat)
        complete_categories = [[], [], [], [], [], []]
        for i in range(0, len(cat_holder)):
            if cat_holder[i].parent is not None:
                complete_categories[i].append(cat_holder[i])
                while cat_holder[i].parent is not None:
                    complete_categories[i].append(cat_holder[i].parent)
                    cat_holder[i] = cat_holder[i].parent
            else:
                complete_categories[i].append(cat_holder[i])
        final = []
        for i in complete_categories:
            if i != []:
                final.append(CategorySimpleSerializer(i, many=True).data)
        return final

    def get_has_available_notif(self, obj: Book):
        return AvailableNotification.objects.filter(user=self.context['user'], book=obj).exists()

    def get_has_borrowed(self, obj: Book):
        return History.objects.filter(user=self.context['user'],
                                      book=obj,
                                      is_active=True,
                                      is_accepted=True).exists()

    def get_has_sent_request(self, obj: Book):
        return Request.objects.filter(user=self.context['user'],
                                      is_accepted__isnull=True,
                                      type='BR').exists()

    def get_is_available(self, obj: Book):
        return obj.count > 0

    def get_deadline(self, obj: Book):
        history = History.objects.filter(book=obj,
                                         user=self.context['user'],
                                         is_active=True,
                                         is_accepted=True)
        if history.exists():
            return (history.first().end_date - date.today()).days
        return None

    category = serializers.SerializerMethodField(method_name='get_category')
    bookComment = CommentSerializer(many=True)
    is_available = serializers.SerializerMethodField(method_name='get_is_available')
    has_available_notif = serializers.SerializerMethodField(method_name='get_has_available_notif')
    has_borrowed = serializers.SerializerMethodField(method_name='get_has_borrowed')
    deadline = serializers.SerializerMethodField(method_name='get_deadline')
    has_sent_request = serializers.SerializerMethodField(method_name='get_has_sent_request')


class MainPageSerializer(serializers.Serializer):

    def get_new_books(self, obj):
        context = {'request': self.context.get('request')}
        return BookSimpleSerializer(Book.objects.all().order_by('-created_at')[:10], many=True, context=context).data

    def get_popular_books(self, obj):
        context = {'request': self.context.get('request')}
        return BookSimpleSerializer(Book.objects.all().order_by('-bookRate')[:10], many=True, context=context).data

    def get_most_borrowed(self, obj):
        context = {'request': self.context.get('request')}
        return BookSimpleSerializer(Book.objects.all().order_by('-wanted_to_read')[:10], many=True,
                                    context=context).data

    new_books = serializers.SerializerMethodField(method_name='get_new_books')
    popular_books = serializers.SerializerMethodField(method_name='get_popular_books')
    most_borrowed_books = serializers.SerializerMethodField(method_name='get_most_borrowed')

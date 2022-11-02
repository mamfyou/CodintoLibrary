import re
from django.contrib.auth import get_user_model
from rest_framework import serializers

from books.models import Book, Comment
from .models import Bookshelf
from process.models import History, Notification


class PanelMainPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'picture', 'first_name', 'last_name']


class PanelProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'picture', 'first_name', 'last_name', 'email', 'username', 'telegram_id', 'phone_number']

    def validate(self, data):
        farsi_pattern = re.compile(r'[\u0600-\u06FF]+')
        signs = re.compile(r'[!@#$%^&*()_+{}":;\']')
        if re.search('[a-zA-Z]', data['first_name']):
            raise serializers.ValidationError('نام نمیتواند شامل حروف انگلیسی باشد!😉')
        elif re.search(signs, data.get('username')):
            raise serializers.ValidationError('نام کاربری فقط باید از حروف انگلیسی یا اعداد تشکیل شده باشد!')
        elif re.search(farsi_pattern, data.get('username')):
            raise serializers.ValidationError('نام کاربری فقط باید از حروف انگلیسی یا اعداد تشکیل شده باشد!')
        elif re.search('[a-zA-Z]', data.get('last_name')):
            raise serializers.ValidationError('نام خانوادگی نمیتواند شامل حروف انگلیسی باشد!😉')
        elif data.get('picture') is not None:
            if data.get('picture').size > 5000000:
                raise serializers.ValidationError('حجم عکس نباید بیشتر از ۵ مگابایت باشد!')
        elif not re.fullmatch(r'09\d{9}', data.get('phone_number')):
            raise serializers.ValidationError('شماره تلفن همراه شما معتبر نیست!')
        elif re.search('۱۲۳۴۵۶۷۸۹۰', data.get('phone_number')):
            raise serializers.ValidationError('شماره تلفن را به صورت اعداد انگلیسی وارد نمایید!')
        elif not re.fullmatch(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', data.get('email')):
            raise serializers.ValidationError('ایمیل شما معتبر نیست!')
        return data


class PanelBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'thumbnail', 'name', 'author', 'created_at']

    thumbnail = serializers.SerializerMethodField(method_name='get_thumbnail')

    def get_thumbnail(self, obj):
        book = Book.objects.get(id=obj.id)
        request = self.context['request']
        photo_url = book.thumbnail.url
        return request.build_absolute_uri(photo_url)

    def get_end_date(self, obj):
        return History.objects.get(book=obj, is_active=True, is_accepted=True).end_date


class BookSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'thumbnail', 'name', 'author']

    thumbnail = serializers.SerializerMethodField(method_name='get_thumbnail')

    def get_thumbnail(self, obj):
        book = Book.objects.get(id=obj.id)
        request = self.context['request']
        photo_url = book.thumbnail.url
        return request.build_absolute_uri(photo_url)


class CommentPanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['book', 'comment']

    comment = serializers.CharField(source='text')
    book = BookSimpleSerializer()


class PanelCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'thumbnail', 'name', 'author', 'bookComment']

    # comment = serializers.SerializerMethodField(method_name='get_end_date')
    thumbnail = serializers.SerializerMethodField(method_name='get_thumbnail')

    def get_thumbnail(self, obj):
        book = Book.objects.get(id=obj.id)
        request = self.context['request']
        photo_url = book.thumbnail.url
        return request.build_absolute_uri(photo_url)


class PanelNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'description', 'is_read', 'book_thumbnail']
        read_only_fields = ['id', 'type', 'title', 'description', 'book_thumbnail']

    def get_book_thumbnail(self, obj):
        if obj.metadata is not None:
            book = Book.objects.get(id=obj.metadata.get('book'))
            request = self.context['request']
            photo_url = book.thumbnail.url
            return request.build_absolute_uri(photo_url)
        return None

    def validate(self, attrs):
        notif = Notification.objects.get(id=self.instance.id)
        if attrs.get('is_read') is False:
            raise serializers.ValidationError('نمیتوانید پیام خوانده شده رو خوانده نشده کنید!')
        elif notif.is_read is True:
            raise serializers.ValidationError('این پیام قبلا خوانده شده است!')
        return attrs

    book_thumbnail = serializers.SerializerMethodField(method_name='get_book_thumbnail')


class PanelBookshelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookshelf
        fields = ['id', 'name', 'book', 'user']
        read_only_fields = ['user']

    def create(self, validated_data):
        bookshelf = Bookshelf.objects.create(name=validated_data.get('name'), user=self.context['user'])
        bookshelf.book.set(validated_data.get('book'))
        return bookshelf

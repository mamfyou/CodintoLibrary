import re
from datetime import date, datetime, timedelta

from django.db.models import F, Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from books.models import Book, BookCategory, Comment, Rate, LikeHistory, DislikeHistory
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
                  'has_borrowed', 'deadline', 'has_sent_request', 'has_commented']

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

    def get_has_commented(self, obj: Book):
        return History.objects.filter(user=self.context['user'],
                                      book=obj,
                                      is_active=False,
                                      is_accepted=True).exists()

    category = serializers.SerializerMethodField(method_name='get_category')
    bookComment = CommentSerializer(many=True)
    is_available = serializers.SerializerMethodField(method_name='get_is_available')
    has_available_notif = serializers.SerializerMethodField(method_name='get_has_available_notif')
    has_borrowed = serializers.SerializerMethodField(method_name='get_has_borrowed')
    deadline = serializers.SerializerMethodField(method_name='get_deadline')
    has_sent_request = serializers.SerializerMethodField(method_name='get_has_sent_request')
    has_commented = serializers.SerializerMethodField(method_name='get_has_commented')


class BookBorrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'thumbnail', 'name', 'author', 'end_date']
        read_only_fields = ['id', 'thumbnail', 'name', 'author']

    end_date = serializers.IntegerField(write_only=True)
    thumbnail = serializers.SerializerMethodField(method_name='get_thumbnail')

    def get_thumbnail(self, obj):
        book = Book.objects.get(id=self.context['book_id'])
        request = self.context['request']
        photo_url = book.thumbnail.url
        return request.build_absolute_uri(photo_url)

    def create(self, validated_data):
        book = Book.objects.get(id=self.context['book_id'])
        History.objects.create(
            user=self.context['user'],
            book=book,
            start_date=date.today(),
            end_date=datetime.now() + timedelta(days=validated_data['end_date']),
        )
        Request.objects.create(
            type='BR',
            user=self.context['user'],
            book=book,
            metadata=validated_data
        )
        return validated_data

    def validate(self, data):
        book = Book.objects.get(id=self.context['book_id'])
        has_request = Request.objects.filter(user=self.context['user'],
                                             is_accepted__isnull=True, )

        has_book = History.objects.filter(user=self.context['user'],
                                          is_active=True,
                                          is_accepted=True)
        if data.get('end_date') not in [14, 30]:
            raise ValidationError('تاریخ انتخاب شده صحیح نمیباشد')
        elif book.count == 0:
            raise ValidationError('کتاب مورد نظر موجود نمیباشد')
        elif has_request.filter(book_id=self.context['book_id']).exists():
            raise ValidationError('شما یک بار برای این کتاب ثبت درخواست کرده اید! لطفا تا پاسخگویی ادمین صبور باشید 🙏')
        elif has_book.filter(book_id=self.context['book_id']).exists():
            raise ValidationError('شما این کتاب را به امانت برده اید!')
        elif has_request.filter(type='BR').count() + has_book.count() >= 2:
            raise ValidationError('شما تا الان دو کتاب تایید شده یا در انتظار تایید دارید!')
        return data


class BookExtendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'thumbnail', 'name', 'author', 'extend_time']
        read_only_fields = ['id', 'thumbnail', 'name', 'author']

    extend_time = serializers.IntegerField(write_only=True)
    thumbnail = serializers.SerializerMethodField(method_name='get_thumbnail')

    def get_thumbnail(self, obj: Book):
        book = Book.objects.get(id=self.context['book_id'])
        request = self.context['request']
        photo_url = book.thumbnail.url
        return request.build_absolute_uri(photo_url)

    def create(self, validated_data):
        book = Book.objects.get(id=self.context['book_id'])
        Request.objects.create(
            type='EX',
            user=self.context['user'],
            book=book,
            metadata=validated_data,
        )
        return validated_data

    def validate(self, data):
        book = Book.objects.get(id=self.context['book_id'])
        has_book = History.objects.filter(user=self.context['user'],
                                          book=book,
                                          is_active=True,
                                          is_accepted=True)
        has_request = Request.objects.filter(is_accepted__isnull=True,
                                             user=self.context['user'],
                                             book=book)
        if not has_book.exists():
            raise ValidationError('شما هنوز این کتاب را به امانت نبرده اید!')
        elif has_book.filter(is_extended=True).exists():
            raise ValidationError('شما یک بار این کتاب را تمدید کرده اید!')
        elif has_request.filter(type='EX').exists():
            raise ValidationError('شما یک بار برای این کتاب ثبت درخواست کرده اید! لطفا تا پاسخگویی ادمین صبور باشید 🙏')
        elif has_request.filter(type__in=['RT', 'EX', 'BR']).exists():
            raise ValidationError('شما یک درخواست دیگر برای این کتاب دارید! لطفا تا پاسخگویی ادمین صبور باشید 🙏')
        return data


class BookReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'thumbnail', 'name', 'author', 'rate', 'comment', 'is_not_read']
        read_only_fields = ['id', 'thumbnail', 'name', 'author']

    thumbnail = serializers.SerializerMethodField(method_name='get_thumbnail')
    rate = serializers.IntegerField(write_only=True, required=False)
    comment = serializers.CharField(write_only=True, required=False)
    is_not_read = serializers.BooleanField(write_only=True)

    def get_thumbnail(self, obj):
        book = Book.objects.get(id=self.context['book_id'])
        request = self.context['request']
        photo_url = book.thumbnail.url
        return request.build_absolute_uri(photo_url)

    def create(self, validated_data):
        Request.objects.create(
            type='RT',
            user=self.context['user'],
            book_id=self.context['book_id'],
        )
        if validated_data.get('is_not_read') is False:
            Request.objects.create(
                type='CM',
                user=self.context['user'],
                book_id=self.context['book_id'],
                metadata={'rate': validated_data['rate'], 'comment': validated_data['comment']}
            )
        return validated_data

    def validate(self, data):
        book = Book.objects.get(id=self.context['book_id'])
        has_book = History.objects.filter(user=self.context['user'],
                                          book=book,
                                          is_active=True,
                                          is_accepted=True)
        has_request = Request.objects.filter(is_accepted__isnull=True,
                                             user=self.context['user'],
                                             book=book)
        if data.get('is_not_read') is False and (data.get('rate') is None or data.get('comment') is None):
            raise ValidationError('لطفا امتیاز و نظر خود را وارد کنید!')
        elif data.get('is_not_read') is True and (data['rate'] is not None or data['comment'] is not None):
            raise ValidationError('شما نمیتوانید بدون خواندن کتاب به آن نظر دهید!')
        elif data.get('rate') not in [1, 2, 3, 4, 5]:
            raise ValidationError('امتیاز باید عدد صحیحی بین 1 تا 5 باشد!')
        elif re.search(r'[a-zA-Z]', data.get('comment')):
            raise ValidationError('نظر شما باید به زبان فارسی باشد!')
        elif not has_book.exists():
            raise ValidationError('شما هنوز این کتاب را به امانت نبرده اید!')
        elif has_request.filter(type='RT').exists():
            raise ValidationError('شما یک بار برای این کتاب ثبت درخواست کرده اید! لطفا تا پاسخگویی ادمین صبور باشید 🙏')
        elif has_request.filter(type__in=['RT', 'EX', 'BR']).exists():
            raise ValidationError('شما یک درخواست دیگر برای این کتاب دارید! لطفا تا پاسخگویی ادمین صبور باشید 🙏')
        return data


class BookCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['rate', 'id', 'user', 'book', 'text', 'created_at', 'Rate', 'like_count', 'dislike_count']
        read_only_fields = ['id', 'user', 'book', 'created_at', 'Rate', 'like_count', 'dislike_count']

    def get_book_rate(self, obj):
        rate_obj = Rate.objects.filter(user=self.context['user'], book_id=self.context['book_id'])
        if rate_obj.exists():
            return rate_obj.first().rate
        return None

    Rate = serializers.SerializerMethodField(method_name='get_book_rate')
    rate = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        Request.objects.create(user=self.context['user'], book=Book.objects.get(id=self.context['book_id']), type='CM',
                               metadata=validated_data)
        return validated_data

    def validate(self, data):
        if data.get('rate') not in [1, 2, 3, 4, 5]:
            raise ValidationError('امتیاز باید عدد صحیحی بین 1 تا 5 باشد!')
        elif re.search(r'[a-zA-Z]', data.get('text')):
            raise ValidationError('نظر شما باید به زبان فارسی باشد!')
        elif Request.objects.filter(type='CM', user=self.context['user'], book_id=self.context['book_id']).exists():
            raise ValidationError('شما یک درخواست کامنت ثبت کرده اید! لطفا تا پاسخگویی ادمین صبور باشید 🙏')
        return data


class CommentFeedbackSerializer(serializers.Serializer):
    like = serializers.BooleanField()
    dislike = serializers.BooleanField()

    def update(self, obj, validated_data):
        like_queryset = LikeHistory.objects.filter(user=self.context.get('user'),
                                                   comment_id=self.context.get('comment'))
        dislike_queryset = DislikeHistory.objects.filter(user=self.context.get('user'),
                                                         comment_id=self.context.get('comment'))
        comment_obj = Comment.objects.filter(id=self.context.get('comment'))
        if validated_data.get('like'):
            if like_queryset.exists():
                comment_obj.update(like_count=F('like_count') - 1)
                like_queryset.delete()
            else:
                if dislike_queryset.exists():
                    comment_obj.update(dislike_count=F('dislike_count') - 1)
                    dislike_queryset.delete()
                comment_obj.update(like_count=F('like_count') + 1)
                LikeHistory.objects.create(user=self.context.get('user'), comment=comment_obj.first())
        elif validated_data.get('dislike'):
            if dislike_queryset.exists():
                comment_obj.update(dislike_count=F('like_count') - 1)
                dislike_queryset.delete()
            else:
                if like_queryset.exists():
                    comment_obj.update(like_count=F('like_count') - 1)
                    like_queryset.delete()
                comment_obj.update(dislike_count=F('like_count') + 1)
                DislikeHistory.objects.create(user=self.context.get('user'), comment=comment_obj.first())
        return validated_data

    def validate(self, data):
        if data.get('like') is True and data.get('dislike') is True:
            raise ValidationError('نمیتوانید همزمان هم لایک هم دیسلایک کنید!')
        return data


class MainPageSerializer(serializers.Serializer):

    def get_new_books(self, obj):
        context = {'request': self.context.get('request')}
        return BookSimpleSerializer(Book.objects.all().order_by('-created_at')[:10], many=True, context=context).data

    def get_popular_books(self, obj):
        context = {'request': self.context.get('request')}
        queryset = Book.objects.annotate(avg_rate=Avg('bookRate__rate')).order_by('-avg_rate')
        return BookSimpleSerializer(queryset[:10], many=True, context=context).data

    def get_most_borrowed(self, obj):
        context = {'request': self.context.get('request')}
        return BookSimpleSerializer(Book.objects.all().order_by('-wanted_to_read')[:10], many=True,
                                    context=context).data

    new_books = serializers.SerializerMethodField(method_name='get_new_books')
    popular_books = serializers.SerializerMethodField(method_name='get_popular_books')
    most_borrowed_books = serializers.SerializerMethodField(method_name='get_most_borrowed')


class BookSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'name', 'author', 'owner', 'publisher']


class AvailableNotifSerializer(serializers.Serializer):
    def create(self, validated_data):
        print(self.context.get('book_id'))
        book = Book.objects.get(id=self.context.get('book_id'))
        if AvailableNotification.objects.filter(user=self.context['user'], book=book).exists():
            AvailableNotification.objects.get(user=self.context['user'], book=book).delete()
            return Response({'message': 'اعلان آماده شدن کتاب غیرفعال شد!'})
        AvailableNotification.objects.create(user=self.context['user'], book=book)
        return Response({'message': 'اعلان آماده شدن کتاب فعال شد!'})

import re
from datetime import datetime, timedelta, date

from django.contrib.auth import get_user_model
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from books.models import Book, Comment, Rate, BookCategory
from books.serializer import CategoryMultipleParentSerializer
from process.models import Request, History, Notification
from process.signals import available_book, new_general_notif


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'confirm_password', 'phone_number', 'email',
                  'telegram_id', 'picture', 'is_superuser', 'is_staff', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True},
            'picture': {'read_only': True},
            'is_superuser': {'read_only': True},
            'is_staff': {'read_only': True},
            'is_active': {'read_only': True},
        }

    confirm_password = serializers.CharField(max_length=128, write_only=True)

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = get_user_model().objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = True
        user.is_staff = True
        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop('confirm_password')
        instance.set_password(validated_data['password'])
        instance.is_active = True
        instance.is_staff = True
        instance.save()
        return super().update(instance, validated_data)
    def validate_first_name(self, value):
        if re.search('[a-zA-Z]', self.initial_data['first_name']):
            raise serializers.ValidationError('نام نمیتواند شامل حروف انگلیسی باشد!😉')
        return value

    def validate_last_name(self, data):
        if re.search('[a-zA-Z]', self.initial_data['last_name']):
            raise serializers.ValidationError('نام خانوادگی نمیتواند شامل حروف انگلیسی باشد!😉')
        return data

    def validate_username(self, data):
        farsi_pattern = re.compile(r'[\u0600-\u06FF]+')
        signs = re.compile(r'[!@#$%^&*()_+{}":;\']')
        print(data)
        if re.search(signs, self.initial_data['username']):
            raise serializers.ValidationError('نام کاربری فقط باید از حروف انگلیسی یا اعداد تشکیل شده باشد!')
        elif re.search(farsi_pattern, self.initial_data['username']):
            raise serializers.ValidationError('نام کاربری فقط باید از حروف انگلیسی یا اعداد تشکیل شده باشد!')
        return data

    def validate_phone_number(self, data):
        if not re.fullmatch(r'09\d{9}', self.initial_data['phone_number']):
            raise serializers.ValidationError('شماره تلفن همراه شما معتبر نیست!')
        elif re.search('۱۲۳۴۵۶۷۸۹۰', self.initial_data['phone_number']):
            raise serializers.ValidationError('شماره تلفن را به صورت اعداد انگلیسی وارد نمایید!')
        return data

    def validate_password(self, data):
        farsi_pattern = re.compile(r'[\u0600-\u06FF]+')
        signs = re.compile(r'[!@#$%^&*()_+{}":;\']')
        common_passwords = ['123456', '123456789', 'qwerty', 'password', 'P@ssw0rd', 'Password', '12345678', '111111',
                            '1234567890', '1234567']
        if self.initial_data['password'] != self.initial_data.get('confirm_password'):
            raise serializers.ValidationError('رمز عبور و تکرار آن یکسان نیستند!')

        elif len(self.initial_data['password']) < 8:
            raise serializers.ValidationError('رمز عبور باید حداقل ۸ کاراکتر باشد!')

        elif re.search(farsi_pattern, self.initial_data['password']):
            raise serializers.ValidationError('رمز عبور نمیتواند شامل حروف فارسی باشد!')
        elif not re.search(signs, self.initial_data['password']):
            raise serializers.ValidationError('رمز عبور باید حداقل از یک نماد تشکیل شده باشد!')
        elif self.initial_data['password'] in common_passwords:
            raise serializers.ValidationError('رمز عبور شما خیلی ساده است!')
        elif self.initial_data.get('first_name') in self.initial_data['password'] or self.initial_data.get('last_name') in self.initial_data['password']:
            raise serializers.ValidationError('رمز عبور نباید شامل نام شما باشد!')
        return self.initial_data['password']

    def validate(self, data):
        self.validate_username(data)
        self.validate_first_name(data)
        self.validate_last_name(data)
        self.validate_phone_number(data)
        self.validate_password(data)
        return super().validate(data)


class BookRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'thumbnail', 'name', 'author', 'publisher']


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'username', 'picture']


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['id', 'user', 'book', 'type', 'metadata', 'is_accepted', 'is_read', 'created']
        read_only_fields = ['user', 'book', 'metadata', 'type', 'created']

    book = BookRequestSerializer(read_only=True)
    is_accepted = serializers.BooleanField(allow_null=True)
    is_read = serializers.BooleanField(write_only=True, default=True)
    user = UserSimpleSerializer(read_only=True)

    def validate(self, data):
        if data.get('is_read') is True and self.instance.is_read is True:
            raise serializers.ValidationError('این درخواست قبلا خوانده شده است!')
        elif data.get('is_read') is False and self.instance.is_read is False:
            raise serializers.ValidationError('این درخواست قبلا به عنوان خوانده نشده ثبت شده است!')
        elif self.instance.is_accepted is not None:
            raise serializers.ValidationError('این درخواست قبلا پاسخ داده شده است!')
        elif data.get('is_accepted') is False and self.instance.type == 'RT':
            raise serializers.ValidationError('امکان رد درخواست بازگشت وجود ندارد!')
        return data

    def update(self, instance: Request, validated_data):
        if validated_data.get('is_accepted') is True:
            instance.is_read = True
            instance.is_accepted = True
            instance.save()
        elif validated_data.get('is_accepted') is False:
            instance.is_read = True
            instance.is_accepted = False
            instance.save()
        if instance.type == 'BR':
            history = History.objects.filter(user=instance.user, book=instance.book, is_active=True,
                                             is_accepted=False).first()
            if validated_data.get('is_accepted'):
                if validated_data.get('is_accepted') is True and history.book.count >= 1:
                    book = history.book
                    history.end_date = datetime.now() + timedelta(days=instance.metadata.get('end_date'))
                    history.start_date = datetime.now()
                    history.is_accepted = True
                    history.is_active = True
                    history.book.count -= 1
                    history.book.wanted_to_read += 1
                    history.save()
                    history.book.save()
                    Notification.objects.create(user=instance.user, picture=instance.book.thumbnail, type='BR',
                                                title='امانت کتاب',
                                                description=f'تایید شد😍' + f'{instance.book.name}' + f'درخواست شما برای امانت کتاب ')

                elif validated_data.get('is_accepted') is False or history.book.count == 0:
                    history.delete()
                    Notification.objects.create(user=instance.user, picture=instance.book.thumbnail, type='BR',
                                                title='امانت کتاب',
                                                description=f'تایید نشد😢' + f'{instance.book.name}' + f'متاسفانه درخواست شما برای امانت کتاب ')
        elif instance.type == 'EX':
            history = History.objects.get(user=instance.user, picture=instance.book.thumbnail, is_active=True,
                                          is_accepted=True)
            if validated_data.get('is_accepted') is True:
                history.end_date += timedelta(days=instance.metadata.get('extend_time'))
                history.is_extended = True
                history.save()
                Notification.objects.create(user=instance.user, picture=instance.book.thumbnail, type='EX',
                                            title='تمدید کتاب',
                                            description=f'تایید شد😍' + f'{instance.book.name}' + f'درخواست شما برای تمدید کتاب ')
            elif validated_data.get('is_accepted') is False:
                Notification.objects.create(user=instance.user, picture=instance.book.thumbnail, type='EX',
                                            title='تمدید کتاب',
                                            description=f'تایید نشد😢' + f'{instance.book.name}' + f'متاسفانه درخواست شما برای تمدید کتاب ')

        elif instance.type == 'RT':
            history = History.objects.filter(user=instance.user, book=instance.book, is_active=True,
                                             is_accepted=True).first()
            if validated_data.get('is_accepted') is True:
                instance.book.count += 1
                instance.book.save()
                history.is_active = False
                history.end_date = datetime.today()
                history.save()
                if instance.book.count == 1:
                    available_book.send_robust(sender=self.__class__, picture=instance.book.thumbnail)
                Notification.objects.create(user=instance.user, picture=instance.book.thumbnail, type='RT',
                                            title='بازگشت کتاب',
                                            description=f'تایید شد😍 امیدواریم تجربه خوبی در کتابخانه کدینتو کسب کرده باشید😊' + f'{instance.book.name}' + f'درخواست شما برای تحویل کتاب ')

        elif instance.type == 'CM':
            if validated_data.get('is_accepted') is True:
                if Comment.objects.filter(user=instance.user, book=instance.book).exists():
                    comment = Comment.objects.get(user=instance.user, book=instance.book)
                    comment.text = instance.metadata.get('comment')
                    comment.save()
                    if Rate.objects.filter(user=instance.user, book=instance.book).exists():
                        if instance.metadata.get('rate') is not None:
                            rate = Rate.objects.get(user=instance.user, book=instance.book)
                            rate.rate = instance.metadata.get('rate')
                            rate.save()
                else:
                    comment = Comment.objects.create(user=instance.user, book=instance.book,
                                                     text=instance.metadata.get('comment'))
                    comment.save()
                    if instance.metadata.get('rate') is not None:
                        rate = Rate.objects.create(user=instance.user, book=instance.book)
                        self.save = rate.save()
                Notification.objects.create(user=instance.user,
                                            title='ثبت نظر',
                                            picture=instance.book.thumbnail, type='CM',
                                            description=f'{comment.text}' + f'کامنت:' + f'ثبت شد' + f'{instance.book.name}' + f'نظر شما برای کتاب ')
            elif validated_data.get('is_accepted') is False:
                Notification.objects.create(user=instance.user,
                                            title='ثبت نظر',
                                            picture=instance.book.thumbnail, type='CM',
                                            description=f'{instance.metadata.get("text")}' + f'کامنت:' + f'تایید نشد' + f'{instance.book.name}' + f'نظر شما برای کتاب')
        return validated_data.get('is_accepted')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCategory
        fields = ['id', 'name', 'parent']


class BookSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'name', 'owner_name', 'publisher', 'publish_date', 'volume_num', 'page_count', 'author',
                  'translator', 'description', 'category', 'categories', 'picture', 'count', 'owner']
        extra_kwargs = {
            'category': {'write_only': True},
            'owner': {'write_only': True},
        }

    category = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    categories = serializers.SerializerMethodField(method_name='get_category', read_only=True)
    owner_name = serializers.StringRelatedField(read_only=True, source='owner')

    def get_category(self, obj: Book):
        return CategoryMultipleParentSerializer(obj.category.all(), many=True).data

    def create(self, validated_data):
        category_names = validated_data.pop('category', [])
        book = Book.objects.create(**validated_data)
        for category_name in category_names:
            BookCategory.objects.get(id=category_name)
            book.category.add(category_name)
        return book

    def validate(self, data):
        persian_letters = re.compile(r'[\u0600-\u06FF]+')
        if data.get('publish_date') >= date.today():
            raise serializers.ValidationError('تاریخ نشر نمیتواند دیر از زمان حال باشد!')
        elif data.get('translator') is not None:
            if not re.search(persian_letters, data.get('translator')):
                raise serializers.ValidationError('نام مترجم باید به فارسی باشد!')
        elif data.get('picture').size >= 5000000:
            raise serializers.ValidationError('سایز عکس نباید بیشتر از ۵ مگابایت باشد!')
        elif data.get('count') == 0:
            raise serializers.ValidationError('تعداد کتاب حداقل ۱ عدد می باشد!')
        return data


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'name', 'author', 'thumbnail']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'description', 'picture']

    def create(self, validated_data):
        new_general_notif.send_robust(sender=self.__class__, title=validated_data.get('title'),
                                      description=validated_data.get('description'),
                                      picture=validated_data['picture'])
        return validated_data

    def validate(self, attrs):
        if not attrs.get('picture'):
            raise serializers.ValidationError('عکس الزامی است!')
        elif attrs['picture'].size > 2 * 1024 * 1024:
            raise serializers.ValidationError('حجم عکس نباید بیشتر از ۲ مگابایت باشد!')
        return attrs


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['id', 'user', 'book', 'start_date', 'end_date', 'is_accepted']

    def get_book_name(self, obj):
        return obj.book.name

    user = serializers.StringRelatedField()
    book = serializers.SerializerMethodField(method_name='get_book_name')

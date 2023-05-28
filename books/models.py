from django.contrib.auth import get_user_model
from django.db import models
import os.path
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class Book(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام کتاب')
    picture = models.ImageField(upload_to='media/book_pic', verbose_name='عکس کتاب')
    thumbnail = models.ImageField(upload_to='media/thumbnails', editable=False, verbose_name='تامبنیل')
    description = models.TextField(verbose_name='توضیحات')
    owner = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='bookOwner', verbose_name='صاحب کتاب')
    author = models.CharField(max_length=100, verbose_name='نویسنده')
    publisher = models.CharField(max_length=100, verbose_name='انتشارات')
    publish_date = models.DateField(verbose_name='تاریخ انتشار')
    translator = models.CharField(max_length=100, null=True, blank=True, verbose_name='مترجم')
    page_count = models.PositiveIntegerField(verbose_name='تعداد صفحات')
    volume_num = models.PositiveIntegerField(verbose_name='شماره جلد')
    count = models.PositiveIntegerField(default=1, verbose_name='تعداد')
    created_at = models.DateField(auto_now_add=True, verbose_name='تاریخ اضافه شدن کتاب')
    category = models.ManyToManyField('BookCategory', related_name='bookCategory', verbose_name='دسته بندی')
    wanted_to_read = models.PositiveIntegerField(default=0, verbose_name='تعداد دفعات خوانده شده')

    def __str__(self):
        return f'{self.name}' + ' - ' + f'{self.author}'

    def save(self, *args, **kwargs):

        if not self.make_thumbnail():
            # set to a default thumbnail
            raise Exception('Could not create thumbnail - is the file type valid?')

        super(Book, self).save(*args, **kwargs)

    def make_thumbnail(self):

        image = Image.open(self.picture)
        image.thumbnail((128, 128), Image.ANTIALIAS)

        thumb_name, thumb_extension = os.path.splitext(self.picture.name)
        thumb_extension = thumb_extension.lower()

        thumb_filename = thumb_name + '_thumb' + thumb_extension

        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False  # Unrecognized file type

        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        # set save=False, otherwise it will run in an infinite loop
        self.thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

        return True


class BookCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام دسته بندی')
    parent = models.ForeignKey('BookCategory', on_delete=models.CASCADE, null=True, blank=True, verbose_name='دسته بندی والد')
    description = models.TextField(verbose_name='توضیحات')
    indent = models.PositiveIntegerField(default=0, verbose_name='تعداد تو در تو')

    def __str__(self):
        return self.name


class Rate(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='userRate', verbose_name='کاربر')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='bookRate', verbose_name='کتاب')
    rate = models.PositiveIntegerField(default=3, verbose_name='امتیاز')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')


class Comment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='userComment', verbose_name='کاربر')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='bookComment', verbose_name='کتاب')
    text = models.TextField(max_length=500, null=True, blank=True, verbose_name='متن')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    like_count = models.PositiveIntegerField(default=0, verbose_name='تعداد لایک')
    dislike_count = models.PositiveIntegerField(default=0, verbose_name='تعداد دیسلایک')

    def __str__(self):
        return str(self.user) + " -> " + str(self.book)


class LikeHistory(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='commentLike', verbose_name='کامنت')
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='likeUser', verbose_name='کاربر')


class DislikeHistory(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='commentDislike', verbose_name='کامنت')
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='DislikeUser', verbose_name='کاربر')


@receiver(pre_save, sender=BookCategory)
def update_indent(sender, instance, **kwargs):
    if instance.parent is not None:
        instance.indent = instance.parent.indent + 1

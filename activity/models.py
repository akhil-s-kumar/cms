from django.db import models
from datetime import date
import uuid
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from imagekit.models import ProcessedImageField
from framework.validators import validate_file_size, processed_image_field_specs

CATEGORY_TYPE = (('CLUB_ACHIEVEMENT', 'CLUB_ACHIEVEMENT'), ('MEMBER_ACHIEVEMENT', 'MEMBER_ACHIEVEMENT'))

class Tags(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='Tag_Author', blank=True, null=True)
    tag = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = "Tags"
        verbose_name = "Tags"

    def __str__(self):
        return self.tag

class News(models.Model):
    def get_poster_path(instance, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        return 'static/uploads/news/cover/' + filename

    title = models.CharField(max_length=100)
    slug = models.SlugField()
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='Author', blank=True, null=True)
    pinned = models.BooleanField()
    cover = ProcessedImageField(default='', verbose_name='News Poster', upload_to=get_poster_path, validators=[validate_file_size], **processed_image_field_specs)
    date = models.DateField(default=date.today)
    categories = models.CharField(max_length=50,choices=CATEGORY_TYPE, default='CLUB_ACHIEVEMENT')
    tags = models.ManyToManyField(Tags, related_name='tags')
    description = RichTextField(max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"

    def __str__(self):
        return self.title

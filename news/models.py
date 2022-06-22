
import time

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Blog(models.Model):
    name = models.CharField(verbose_name="Имя", max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "блог"
        verbose_name_plural = "блоги"


def validate_article_image_file_size(image):
    IMAGE_SIZE_LIMIT = 5 * 2**20
    IMAGE_SIZE_LIMIT_STR = "5 мегабайт"

    if image.file.size > IMAGE_SIZE_LIMIT:
        raise ValidationError("Размер файла изображения превышает {0}".format(IMAGE_SIZE_LIMIT_STR))

def get_article_image_filename(instance, name):
    return "articles/user_{}/{:.3f}_{}".format(
            instance.owner.id, time.time(), name)


class Article(models.Model):



    title = models.CharField(verbose_name="Заголовок", max_length=50)
    image = models.ImageField(
            verbose_name="Изображение",
            upload_to=get_article_image_filename,
            validators=[validate_article_image_file_size],
            )
    text = models.TextField(verbose_name="Текст", blank=False)
    blog = models.ManyToManyField(Blog, verbose_name="Блог")
    owner = models.ForeignKey(User,
            verbose_name="Владелец",
            on_delete=models.CASCADE)

    published_date = models.DateTimeField(
            verbose_name="Дата публикации",
            auto_now_add=True,
            editable=False)

    class Meta:
        verbose_name = "новость"
        verbose_name_plural = "новости"




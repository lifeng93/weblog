from django.db import models
from django.conf import settings

# Create your models here.
class Category(models.Model):
    cate_name = models.CharField(max_length=20)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    def __str__(self):
        return self.cate_name
    class Meta:
        db_table = "category"
        verbose_name_plural = "categories"


class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    title = models.CharField(max_length=255)
    content = models.TextField()
    cate = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    is_public = models.BooleanField(default=False)
    is_public_index = models.BooleanField(default=False)
    reads = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    can_comment = models.BooleanField(default=True)
    is_recycle = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    def __str__(self):
        return self.title
    class Meta:
        db_table = "article"
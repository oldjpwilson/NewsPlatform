from django.db import models
from django.urls import reverse
from tinymce import HTMLField
from categories.models import Category
from core.models import Channel
from .managers import ArticleManager

MEDIA_CHOICES = (
    ('Article', 'article'),
    ('Picture', 'picture'),
    ('Video', 'video')
)


class Duration(models.Model):
    type = models.CharField(max_length=20)
    # update, article, report, documentary
    description = models.TextField()

    def __str__(self):
        return self.type


class Urgency(models.Model):
    type = models.CharField(max_length=20)  # Current, breaking
    description = models.TextField()

    def __str__(self):
        return self.type


class Article(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    thumbnail = models.ImageField(blank=True, null=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_CHOICES)
    published_date = models.DateTimeField(auto_now_add=True)
    last_edit_date = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category)
    urgency = models.ForeignKey(
        Urgency, on_delete=models.SET_NULL, blank=True, null=True)
    duration = models.ForeignKey(
        Duration, on_delete=models.SET_NULL, blank=True, null=True)
    content = HTMLField('Content')  # tinymce
    rating = models.FloatField(default=0)
    view_count = models.IntegerField(default=0)
    draft = models.BooleanField(default=False)

    # comments with disqus
    # location = models.ForeignKey(Location) # TODO: research
    objects = ArticleManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article-detail', kwargs={'id': self.id})

    def get_update_url(self):
        return reverse('article-update', kwargs={'id': self.id})

    def get_delete_url(self):
        return reverse('article-delete', kwargs={'id': self.id})

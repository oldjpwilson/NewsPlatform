from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from star_ratings.models import Rating
from tinymce import HTMLField
from categories.models import Category
from core.models import Channel, User
from .managers import ArticleManager

MEDIA_CHOICES = (
    ('Text and Video', 'Text and Video'),
    ('Text and Picture', 'Text and Picture'),
    ('Text, Picture and Video', 'Text, Picture and Video'),
    ('Text', 'Text'),
    ('Picture', 'Picture'),
    ('Video', 'Video'),
)


class Duration(models.Model):
    type = models.CharField(max_length=80)

    def __str__(self):
        return self.type


class Urgency(models.Model):
    type = models.CharField(max_length=80)

    def __str__(self):
        return self.type


class Article(models.Model):
    channel = models.ForeignKey(
        Channel, related_name='articles', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    thumbnail = models.ImageField(blank=True, null=True)
    media_type = models.CharField(max_length=40, choices=MEDIA_CHOICES)
    published_date = models.DateTimeField(auto_now_add=True)
    last_edit_date = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category)
    urgency = models.ForeignKey(
        Urgency, on_delete=models.SET_NULL, blank=True, null=True)
    duration = models.ForeignKey(
        Duration, on_delete=models.SET_NULL, blank=True, null=True)
    content = HTMLField('Content')  # tinymce
    rating = GenericRelation(
        Rating, related_query_name='articles')

    '''
    related_query_name allows you to query like:
        Rating.objects.filter(articles__title='first article')
    '''

    view_count = models.IntegerField(default=0)
    draft = models.BooleanField(default=False)

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

    def get_view_count(self):
        return ArticleView.objects.filter(article=self).count()

    @property
    def get_rating(self):
        return Rating.objects.get(object_id=self.id)


class ArticleView(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

from django.db import models
from django.db.models.signals import pre_save
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse
from star_ratings.models import Rating
from tinymce import HTMLField
from categories.models import Category
from core.models import Channel, User
from .managers import ArticleManager
from .utils import create_slug

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
    title = models.CharField(max_length=50, blank=False, null=False)
    slug = models.SlugField(blank=True)
    description = models.TextField(help_text="This is a summary of the article and helps with SEO. This should be filled in")
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
    objects = ArticleManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article-detail', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('article-update', kwargs={'slug': self.slug})

    def get_delete_url(self):
        return reverse('article-delete', kwargs={'slug': self.slug})

    def get_view_count(self):
        qs = ArticleView.objects.filter(article=self)
        if qs.exists():
            return qs.count()
        return 0

    @property
    def get_rating(self):
        qs = Rating.objects.filter(object_id=self.id)
        if qs.exists():
            return qs.first()
        return None


class ArticleView(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username


class FreeView(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    channel = models.ForeignKey(
        Channel, on_delete=models.SET_NULL, blank=True, null=True)
    article_view = models.ForeignKey(
        ArticleView, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username


def pre_save_article_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(pre_save_article_receiver, sender=Article)

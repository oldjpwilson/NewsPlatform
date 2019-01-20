from django.db import models
from categories.models import Category
from core.models import Channel


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
    media_type = models.CharField(max_length=10, choices=MEDIA_CHOICES)
    published_date = models.DateTimeField(auto_now_add=True)
    last_edit_date = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category)
    urgency = models.ForeignKey(
        Urgency, on_delete=models.SET_NULL, blank=True, null=True)
    duration = models.ForeignKey(
        Duration, on_delete=models.SET_NULL, blank=True, null=True)
    content = models.TextField()  # tinymce
    rating = models.FloatField(default=0)
    # comments with disqus
    # location = models.ForeignKey(Location) # TODO: research

    def __str__(self):
        return self.title

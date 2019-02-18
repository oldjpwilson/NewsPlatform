from django.db import models
from django.db.models import Avg, Sum
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from categories.models import Category
from .managers import ChannelManager


class User(AbstractUser):
    pass

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    # location_id = models.CharField() # TODO: geodjango?
    stripe_customer_id = models.CharField(max_length=40)
    payment_details = models.CharField(
        max_length=18)  # TODO: store with stripe
    subscriptions = models.ManyToManyField('Channel')

    def __str__(self):
        return self.user.email

    def get_subscription_count(self):
        return self.subscriptions.count()


class Channel(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=20, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    profile_image = models.ImageField()
    background_image = models.ImageField()
    categories = models.ManyToManyField(Category)
    rating = models.FloatField(default=0)
    stripe_account_id = models.CharField(max_length=40)
    stripe_plan_id = models.CharField(max_length=40)
    payment_details = models.CharField(
        max_length=18)  # TODO: store with stripe
    subscribers = models.ManyToManyField(Profile, blank=True)

    objects = ChannelManager()

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('channel-public', kwargs={
            'name': self.name
        })

    def get_latest_articles(self):
        return self.articles.all().order_by('published_date')[:4]

    def get_total_article_views(self):
        return self.articles.all().values('view_count').aggregate(Sum('view_count'))

    @property
    def channel_rating(self):
        return self.articles \
            .filter(rating__isnull=False, rating__count__gt=0) \
            .aggregate(Avg('rating__average'))

    @property
    def subscriber_count(self):
        return self.subscribers.count()

    @property
    def article_count(self):
        return self.articles.count()

    @property
    def categories_count(self):
        return self.categories.count()

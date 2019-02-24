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
    subscribers = models.ManyToManyField(Profile, blank=True)
    # whether they've connected stripe
    visible = models.BooleanField(default=False)

    objects = ChannelManager()

    def __str__(self):
        return self.name

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


class Subscription(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE)
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.profile.user.username


class Payout(models.Model):
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.channel.name

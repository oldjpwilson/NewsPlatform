from django.db import models
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
    middle_names = models.CharField(max_length=30)  # TODO: necessary?
    # TODO: phone length dependent on country
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField(blank=True, null=True)
    # location_id = models.CharField() # TODO: geodjango?
    payment_details = models.CharField(
        max_length=18)  # TODO: max credit card length?
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
    rating = models.FloatField(default=0)
    categories = models.ManyToManyField(Category)
    payment_details = models.CharField(
        max_length=18)  # TODO: max credit card length?
    subscribers = models.ManyToManyField(Profile, blank=True)

    objects = ChannelManager()

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("channel-public", kwargs={
            'name': self.name
        })

    def get_latest_articles(self):
        return self.articles.all().order_by('published_date')[:4]

    @property
    def subscriber_count(self):
        return self.subscribers.count()

    @property
    def article_count(self):
        return self.articles.count()

    @property
    def categories_count(self):
        return self.categories.count()

from django.db import models
from django.contrib.auth.models import AbstractUser
from categories.models import Category
from .managers import ChannelManager


class User(AbstractUser):
    pass

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
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


class Channel(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, unique=True)
    date_joined = models.DateTimeField()
    description = models.TextField()
    profile_image = models.ImageField()
    background_image = models.ImageField()
    rating = models.FloatField()
    categories = models.ManyToManyField(Category)
    payment_details = models.CharField(
        max_length=18)  # TODO: max credit card length?
    subscribers = models.ManyToManyField(Profile)

    objects = ChannelManager()

    def __str__(self):
        return self.user.username

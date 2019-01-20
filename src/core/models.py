from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from categories.models import Category


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
    # TODO: oncreate - date_joined to be same as users
    date_joined = models.DateTimeField()
    description = models.TextField()
    profile_image = models.ImageField()
    background_image = models.ImageField()
    rating = models.FloatField()
    categories = models.ManyToManyField(Category)
    payment_details = models.CharField(
        max_length=18)  # TODO: max credit card length?
    subscribers = models.ManyToManyField(Profile)

    def __str__(self):
        return self.user.email


# Signals

def user_signup_receiver(sender, instance, **kwargs):
    # create the users profile
    profile = Profile.objects.get_or_create(user=instance)
    return profile


post_save.connect(user_signup_receiver, sender=User)

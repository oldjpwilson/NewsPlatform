from django.db import models
from django.contrib.auth.models import AbstractUser


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
    date_of_birth = models.DateField()
    # location_id = models.CharField() # TODO: geodjango?
    payment_details = models.CharField(
        max_length=18)  # TODO: max credit card length?

    def __str__(self):
        return self.user.email


class Channel(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, unique=True)
    # TODO: signal to fill as users default date_joined
    date_joined = models.DateTimeField()
    description = models.TextField()
    profile_image = models.ImageField()
    background_image = models.ImageField()
    rating = models.FloatField()
    payment_details = models.CharField(
        max_length=18)  # TODO: max credit card length?

    def __str__(self):
        return self.user.email

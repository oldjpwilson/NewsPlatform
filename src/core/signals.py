from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from .models import User, Profile


def user_signup_receiver(sender, instance, **kwargs):
    profile = Profile.objects.get_or_create(user=instance)
    return profile


post_save.connect(user_signup_receiver, sender=User)

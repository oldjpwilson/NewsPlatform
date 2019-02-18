from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save

from .utils import Mailchimp


class SignUp(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    email = models.EmailField()
    subscribed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return self.user.username


def new_user_receiver(sender, instance, created, *args, **kwargs):
    if created:
        new_profile, is_created = SignUp.objects.get_or_create(
            user=instance, email=instance.email)

        if new_profile.email != '':
            mc = Mailchimp()
            mc.add_email(new_profile.email)


post_save.connect(new_user_receiver, sender=settings.AUTH_USER_MODEL)

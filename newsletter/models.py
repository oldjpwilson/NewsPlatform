from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from .utils import Mailchimp

User = get_user_model()


class SignUp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    subscribed = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return self.user.username


def new_user_receiver(sender, instance, created, *args, **kwargs):
    if created:
        new_profile = SignUp.objects.get_or_create(
            user=instance, email=instance.email)
        mc = Mailchimp()
        mc.add_email(instance.email)


post_save.connect(new_user_receiver, sender=User)

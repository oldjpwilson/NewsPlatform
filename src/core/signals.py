from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from .models import User, Profile


import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def user_signup_receiver(sender, instance, created, **kwargs):
    # if the user just signed up
    if created:
        profile, created = Profile.objects.get_or_create(user=instance)
        customer = stripe.Customer.create(email=instance.email)
        profile.stripe_customer_id = customer['id']
        profile.save()
        return profile


post_save.connect(user_signup_receiver, sender=User)

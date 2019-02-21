import django
import os
import stripe
from django.conf import settings
from datetime import datetime, timedelta
from channels.models import Subscription, Channel, Payout

os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "newsPlatform.settings.development")
django.setup()

stripe.api_key = settings.STRIPE_SECRET_KEY


def calcuate_payouts(request):
    channels = Channel.objects.all()
    for channel in channels:
        amount = 0
        subscriptions = Subscription.objects.filter(
            channel=channel,
            active=True
        )
        amount = 0.5 * subscriptions.count()  # 50 cents for every subscription

        # transfer from account to channel account

        payout = Payout(channel=channel, amount=amount)
        payout.save()

        stripe.Transfer.create(
            amount=amount,
            currency="usd",
            destination=channel.stripe_account_id,
            stripe_account='platform-stripe-account'
        )

        # send emails to journalists saying they've been paid

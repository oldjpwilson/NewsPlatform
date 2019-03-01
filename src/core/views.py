from datetime import datetime, timedelta
import os
import requests
import stripe
import urllib
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views import View
from star_ratings.models import Rating
from articles.models import Article, ArticleView
from categories.views import get_todays_most_popular_article_categories
from .forms import ChannelCreateUpdateForm
from .models import Profile, Channel, Subscription, Payout
from .helpers import (
    get_profile_current_billing_total,
    get_channel_current_billing_revenue,
    get_channel_alltime_billing_revenue,
    paginate_queryset,
    get_most_viewed_channel,
    get_highest_rated_article,
    get_most_viewed_article,
    send_email
)

stripe.api_key = settings.STRIPE_SECRET_KEY


def check_user_payment_details(user):
    profile_qs = Profile.objects.filter(user=user)
    if profile_qs.exists():
        customer = stripe.Customer.retrieve(profile_qs[0].stripe_customer_id)
        if len(customer.sources) > 0:
            return True
        return False
    return False


def check_user_is_journalist(user):
    try:
        return user.channel
    except:
        return redirect(reverse('my-profile'))


def check_channel_has_stripe_account(channel):
    if channel.stripe_account_id == '' or channel.stripe_account_id is None:
        return None
    return channel.stripe_account_id


def check_channel_status(request):
    channel_qs = Channel.objects.filter(user=request.user)
    if channel_qs.exists():
        return channel_qs[0]
    return None


@login_required
def my_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    articles = Article.objects.get_highest_rated(3)
    queryset, page_request_var = paginate_queryset(request, articles)
    channels = profile.subscriptions.all()
    sub_count = profile.subscriptions.count()
    total_article_views = ArticleView.objects.filter(user=request.user).count()
    most_viewed_channel = get_most_viewed_channel(request.user)
    current_monthly_billing_total = get_profile_current_billing_total(profile)
    context = {
        'profile': profile,
        'queryset': queryset,
        'channel_list': channels,
        'sub_count': sub_count,
        'total_article_views': total_article_views,
        'most_viewed_channel': most_viewed_channel,
        'display': 'stats',
        'current_monthly_billing_total': current_monthly_billing_total,
        'page_request_var': page_request_var
    }
    return render(request, 'core/profile.html', context)


@login_required
def profile_update_account(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form_type = request.POST.get("account_form")
        if form_type == "account_form":
            email = request.POST.get("email")
            old_password = request.POST.get("old_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            username = request.user.username
            user = authenticate(username=username, password=old_password)
            if user is not None:
                if new_password != confirm_password:
                    messages.info(request, "Your passwords did not match.")
                    redirect(reverse('my-profile'))

                elif new_password == confirm_password:
                    user.set_password(confirm_password)
                    user.save()
                    messages.success(
                        request, 'Successfully changed password. Please login to confirm your password change.')
                    redirect(reverse('my-profile'))
            else:
                messages.info(request, "Incorrect Password.")
                return redirect(reverse('my-profile'))

    context = {
        'display': 'edit_account',
        'user': request.user,
    }
    return render(request, 'core/profile.html', context)


@login_required
def profile_update_payment_details(request):
    profile = get_object_or_404(Profile, user=request.user)
    customer = stripe.Customer.retrieve(profile.stripe_customer_id)
    if request.method == "POST":
        token = request.POST['stripeToken']
        if token:
            customer.source = token
            customer.save()
            return redirect(reverse("edit-profile-payment-details"))

    context = {
        'display': 'edit_payment_details',
        'user': request.user,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        'card_list': customer['sources']['data']
    }
    return render(request, 'core/profile.html', context)


@login_required
@user_passes_test(check_user_is_journalist)
def my_channel(request):
    channel = get_object_or_404(Channel, user=request.user)
    articles = channel.articles.all().order_by('-published_date')
    highest_rated_article = get_highest_rated_article(channel)
    most_viewed_article = get_most_viewed_article(channel)
    queryset, page_request_var = paginate_queryset(request, articles)
    current_billing_revenue = get_channel_current_billing_revenue(channel)
    alltime_billing_revenue = get_channel_alltime_billing_revenue(channel)
    context = {
        'channel': channel,
        'queryset': queryset,
        'highest_rated_article': highest_rated_article,
        'most_viewed_article': most_viewed_article,
        'page_request_var': page_request_var,
        'current_billing_revenue': current_billing_revenue,
        'alltime_billing_revenue': alltime_billing_revenue
    }
    return render(request, 'core/channel.html', context)


def channel_list(request):
    channels = Channel.objects.filter(visible=True)
    queryset, page_request_var = paginate_queryset(request, channels)
    most_viewed = Article.objects.get_todays_most_viewed_channels(3)
    most_recent = Article.objects.get_todays_most_recent(3)
    most_popular_cats = get_todays_most_popular_article_categories()
    context = {
        'queryset': queryset,
        'page_request_var': page_request_var,
        'most_viewed': most_viewed,
        'most_recent': most_recent,
        'cats': most_popular_cats
    }
    return render(request, 'core/channel_list.html', context)


def channel_public(request, name):
    channel = get_object_or_404(Channel, name=name)
    articles = channel.articles.all().order_by('-published_date')
    queryset, page_request_var = paginate_queryset(request, articles)
    context = {
        'channel': channel,
        'queryset': queryset,
        'page_request_var': page_request_var
    }
    return render(request, 'core/channel_public.html', context)


@login_required
def channel_create(request):
    channel_status = check_channel_status(request)
    if channel_status is not None:
        messages.info(request, "You already have a channel!")
        return redirect(reverse('my-profile'))
    form = ChannelCreateUpdateForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            channel = form.instance
            channel.user = request.user
            channel.save()
            return redirect(reverse('my-channel'))
    context = {
        'form': form,
    }
    return render(request, 'core/channel_create.html', context)


@login_required
@user_passes_test(check_user_is_journalist)
def channel_stats(request):
    if not request.user.channel:
        return redirect(reverse('profile'))
    channel = get_object_or_404(Channel, user=request.user)
    queryset, page_request_var = paginate_queryset(
        request, channel.articles.all())
    context = {
        'name': channel.name,
        'display': 'stats',
        'total_article_views': channel.get_total_article_views(),
        'queryset': queryset,
        'page_request_var': page_request_var
    }
    return render(request, 'core/channel_update.html', context)


@login_required
@user_passes_test(check_user_is_journalist)
def channel_update(request):
    if not request.user.channel:
        return redirect(reverse('profile'))
    channel = get_object_or_404(Channel, user=request.user)
    form = ChannelCreateUpdateForm(request.POST or None, instance=channel)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.info(request, 'Your channel details have been saved')
            return redirect(reverse('edit-my-channel'))
    context = {
        'form': form,
        'name': channel.name,
        'display': 'edit_channel_details'
    }
    return render(request, 'core/channel_update.html', context)


@login_required
@user_passes_test(check_user_is_journalist)
def channel_update_payment_details(request):
    channel = get_object_or_404(Channel, user=request.user)
    context = {
        'name': channel.name,
        'display': 'edit_payment_details',
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
    }
    return render(request, 'core/channel_update.html', context)


@login_required
def subscribe(request, name):
    profile = get_object_or_404(Profile, user=request.user)
    channel = get_object_or_404(Channel, name=name)

    # redirect if user doesn't have a credit card
    user_has_payment_details = check_user_payment_details(request.user)
    if not user_has_payment_details:
        messages.info(
            request, "Please enter payment details to subscribe to a channel")
        return redirect(reverse("edit-profile-payment-details"))

    # create a customer to subscribe to the journalist
    customer = stripe.Customer.retrieve(profile.stripe_customer_id)

    # create the subscription to the journalists stripe account
    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{"plan": channel.stripe_plan_id}],
    )

    # store the new stripe susbciption
    sub = Subscription()
    sub.profile = profile
    sub.channel = channel
    sub.stripe_subscription_id = subscription.id
    sub.save()

    # update the profile's subscriptions
    profile.subscriptions.add(channel)
    profile.save()

    # update the channels subscribers
    channel.subscribers.add(profile)
    channel.save()

    return redirect(channel.get_absolute_url())


@login_required
def unsubscribe(request, name):
    profile = get_object_or_404(Profile, user=request.user)
    channel = get_object_or_404(Channel, name=name)
    subscription = get_object_or_404(Subscription, profile=profile)

    # update the profile's subscriptions
    profile.subscriptions.remove(channel)
    profile.save()

    # update the channels subscribers
    channel.subscribers.remove(profile)
    channel.save()

    # update the stripe subscription
    sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
    sub.delete()

    # update our record of stripe subscriptions
    subscription.active = False
    subscription.save()

    return redirect(channel.get_absolute_url())


@login_required
def remove_credit_card(request, card_id):
    profile = get_object_or_404(Profile, user=request.user)
    customer = stripe.Customer.retrieve(profile.stripe_customer_id)
    customer.sources.retrieve(card_id).delete()
    return redirect(reverse("edit-profile-payment-details"))


class StripeAuthorizeView(LoginRequiredMixin, View):

    def get(self, request):

        url = 'https://connect.stripe.com/oauth/authorize'
        params = {
            'response_type': 'code',
            'scope': 'read_write',
            'client_id': settings.STRIPE_CONNECT_CLIENT_ID,
            # 'redirect_uri': f'{settings.DOMAIN}/oauth/callback/' # TODO: can only test when live
        }
        url = f'{url}?{urllib.parse.urlencode(params)}'
        return redirect(url)


class StripeAuthorizeCallbackView(View):

    def get(self, request):
        code = request.GET.get('code')
        if code:
            data = {
                'client_secret': settings.STRIPE_SECRET_KEY,
                'grant_type': 'authorization_code',
                'client_id': settings.STRIPE_CONNECT_CLIENT_ID,
                'code': code
            }
            url = 'https://connect.stripe.com/oauth/token'
            resp = requests.post(url, params=data)

            channel = get_object_or_404(Channel, user=request.user)
            plan = stripe.Plan.create(
                id=f"monthly-membership-{journalist_stripe_acc['id']}",
                amount=100,  # 100 cents = $1
                interval="month",
                currency="usd",
                product={
                    "name": f"{channel.name} membership"
                }
            )

            channel.stripe_account_id = resp.json()['stripe_user_id']
            channel.stripe_plan_id = plan['id']
            channel.visible = True
            channel.save()

        response = redirect(reverse('edit-my-channel'))
        return response


def create_payouts(request, key):
    '''
    The payouts calculated in this function return the amount earned in the previous month.
    For example if todays date is the 14th February 2019, the calculated payout is for the period
    between 1 January 2019 and 1 February 2019
    '''

    # if key is not correct - don't create payments
    if settings.PAYMENTS_KEY != key:
        return HttpResponse(status=500)

    try:
        first_day_of_current_month = datetime.now().replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - \
            timedelta(days=1)
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

        channels = Channel.objects.all()

        for channel in channels:
            amount = 0
            # get all subscriptions that started before 1 month ago
            # - but only the ones that are still subscribed

            recurring_subscriptions = Subscription.objects \
                .filter(
                    channel=channel,
                    modified_at__lte=first_day_of_previous_month
                ).exclude(active=False)

            # get subscriptions created in previous month
            new_subscriptions = Subscription.objects \
                .filter(
                    channel=channel,
                    modified_at__range=[
                        first_day_of_previous_month, first_day_of_current_month]
                )

            # update total amount to pay journalist
            amount += 0.5 * (recurring_subscriptions.count() +
                             new_subscriptions.count())

            if amount > 0:
                # transfer from account to journalist account
                stripe.Transfer.create(
                    amount=amount * 100,  # this value is in cents
                    currency="usd",
                    destination=channel.stripe_account_id
                )

                # record it on our side
                payout = Payout(channel=channel, amount=amount)
                payout.save()

                # send email to journalist saying they've been paid
                send_email(
                    "Newsplatform Monthly Payout Receiver",
                    channel.name,
                    f"We've just sent a payout of {amount} to your Stripe account",
                    channel.user.email
                )

        # make sure this is outside the forloop
        return HttpResponse(status=201)
    except:
        return HttpResponse(status=500)

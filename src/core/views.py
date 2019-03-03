from datetime import datetime, timedelta
import os
import requests
import stripe
import urllib
from django.db.models import Count
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views import View
from star_ratings.models import Rating
from articles.models import Article, ArticleView
from categories.views import get_todays_most_popular_article_categories
from .forms import ChannelCreateForm, ChannelUpdateForm
from .models import Profile, Channel, Subscription, Payout, Charge
from .helpers import (
    get_profile_current_billing_total,
    get_channel_current_billing_revenue,
    get_channel_alltime_billing_revenue,
    get_next_date,
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
    next_payment_date = get_next_date(26)
    context = {
        'profile': profile,
        'queryset': queryset,
        'channel_list': channels,
        'sub_count': sub_count,
        'total_article_views': total_article_views,
        'most_viewed_channel': most_viewed_channel,
        'display': 'stats',
        'current_monthly_billing_total': current_monthly_billing_total,
        'page_request_var': page_request_var,
        'next_payment_date': next_payment_date
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
    next_payout_date = get_next_date(15)
    context = {
        'channel': channel,
        'queryset': queryset,
        'highest_rated_article': highest_rated_article,
        'most_viewed_article': most_viewed_article,
        'page_request_var': page_request_var,
        'current_billing_revenue': current_billing_revenue,
        'alltime_billing_revenue': alltime_billing_revenue,
        'next_payout_date': next_payout_date
    }
    return render(request, 'core/channel.html', context)


def channel_list(request):
    channels = Channel.objects.all()
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

    form = ChannelCreateForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            channel = form.save(commit=False)
            channel.user = request.user
            channel.stripe_account_id = None
            channel.save()
            form.save_m2m()
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
    current_billing_revenue = get_channel_current_billing_revenue(channel)
    alltime_billing_revenue = get_channel_alltime_billing_revenue(channel)
    queryset, page_request_var = paginate_queryset(
        request, channel.articles.all())
    next_payout_date = get_next_date(15)
    context = {
        'name': channel.name,
        'display': 'stats',
        'total_article_views': channel.get_total_article_views(),
        'queryset': queryset,
        'current_billing_revenue': current_billing_revenue,
        'alltime_billing_revenue': alltime_billing_revenue,
        'page_request_var': page_request_var,
        'next_payout_date': next_payout_date
    }
    return render(request, 'core/channel_update.html', context)


@login_required
@user_passes_test(check_user_is_journalist)
def channel_update(request):
    if not request.user.channel:
        return redirect(reverse('profile'))
    channel = get_object_or_404(Channel, user=request.user)
    form = ChannelUpdateForm(request.POST or None,
                             request.FILES or None, instance=channel)
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
        'channel': channel,
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

    # store the new stripe susbciption
    sub = Subscription()
    sub.profile = profile
    sub.channel = channel
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

    # update our record of stripe subscriptions
    subscription.active = False
    subscription.save()

    return redirect(channel.get_absolute_url())


@login_required
def remove_credit_card(request, card_id):
    profile = get_object_or_404(Profile, user=request.user)
    customer = stripe.Customer.retrieve(profile.stripe_customer_id)
    # TODO: prevent if user has outstanding bill

    # if their last charge was last month, then they still owe this month

    # don't let them remove the card - show a button that says pay now or add a new card
    customer.sources.retrieve(card_id).delete()
    return redirect(reverse("edit-profile-payment-details"))


class StripeAuthorizeView(LoginRequiredMixin, View):

    def get(self, request):
        channel = get_object_or_404(Channel, user=request.user)
        if channel.subscribers.count() < 20:
            messages.info(
                request, "You need more than 20 subscribers to start receiving payouts")
            return redirect(reverse('edit-channel-payment-details'))

        url = 'https://connect.stripe.com/oauth/authorize'
        params = {
            'response_type': 'code',
            'scope': 'read_write',
            'client_id': settings.STRIPE_CONNECT_CLIENT_ID,
            'redirect_uri': f'{settings.DOMAIN}/stripe/callback/'
        }
        url = f'{url}?{urllib.parse.urlencode(params)}'
        return redirect(url)


class StripeAuthorizeCallbackView(View):

    def get(self, request):
        try:
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
                channel.stripe_account_id = resp.json()['stripe_user_id']
                channel.connected = True
                channel.save()

            messages.info(
                request, "Your Stripe account was successfully linked!")
            response = redirect(reverse('edit-my-channel'))
            return response

        except:
            messages.error(
                request, "There was an error connecting your Stripe account. If the error persists please contact support.")
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
        channels = Channel.objects \
            .filter(connected=True) \
            .annotate(num_subs=Count('subscribers')) \
            .filter(num_subs__gte=20)

        for channel in channels:
            amount = get_channel_current_billing_revenue(channel)
            if amount > 0:
                # transfer from account to journalist account
                try:
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

                except Exception as e:
                    # record it on our side
                    payout = Payout(channel=channel,
                                    amount=amount,
                                    success=False)
                    payout.save()

        # make sure this is outside the forloop
        return HttpResponse(status=201)
    except:
        # send email to alert us
        send_email(
            "Newsplatform Monthly Payout Receiver Alert",
            "Admin"
            f"Failed attempt to payout to Stripe account. Investigate ASAP",
            settings.ADMIN_EMAIL
        )
        return HttpResponse(status=500)


def bill_customers(request, key):
    '''
    The charges calculated in this function return the amount each customer owes for the previous month. 
    This script runs on the 26th of each month and calculates the number of new subscriptions between the
    26th day of the last month and this month. It then adds the recurring subscriptions from outside the
    previous months period.
    '''

    # if key is not correct - don't bill customers
    if settings.BILL_KEY != key:
        return HttpResponse(status=500)

    try:
        profiles = Profile.objects.all()
        for profile in profiles:
            amount = get_profile_current_billing_total(profile)
            if amount > 0:

                try:
                    # charge the customer once
                    # TODO: prevent user not having a credit card
                    charge = stripe.Charge.create(
                        amount=int(amount * 100),  # this value is in cents
                        currency="usd",
                        customer=profile.stripe_customer_id
                    )

                    # record it on our side
                    charge = Charge(
                        profile=profile,
                        amount=amount,
                        stripe_charge_id=charge.id
                    )
                    charge.save()

                    # send email to user saying they've been charged
                    send_email(
                        "Newsplatform Invoice",
                        profile.user.username,
                        f"Thank you for using NewsPlatform. \
                        We've successfully charged your credit card an amount of ${amount} \
                        for the previous month's subscriptions.",
                        profile.user.email
                    )

                except Exception as e:
                    # create an alert because this failed
                    charge = Charge(
                        profile=profile,
                        amount=amount,
                        success=False
                    )
                    charge.save()

                    # send email to alert the user
                    send_email(
                        "Newsplatform Invoice",
                        profile.user.username,
                        f"We've failed to bill you for your subscriptions on NewsPlatform. \
                        Please login and add a credit card to your account.",
                        profile.user.email
                    )

        # make sure this is outside the forloop
        return HttpResponse(status=201)
    except Exception as e:
        # send email to alert us
        send_email(
            "Newsplatform Monthly Payout Receiver Alert",
            "Admin"
            f"Failed attempt to payout to Stripe account. Error message: {e}",
            settings.ADMIN_EMAIL
        )
        return HttpResponse(status=500)


def close_profile(request):
    user = request.user
    channel_status = check_channel_status(request)
    if channel_status is not None:
        messages.info(
            request, "You cannot delete your account without closing your channel first.")
        return redirect(reverse('my-channel'))
    user.is_active = False
    user.save()
    logout(request)
    messages.success(request, 'Account successfully closed.')
    send_email(
        "NewsPlatform account closure",
        user.username,
        "Your NewsPlatform account has successfully been closed",
        user.email
    )
    return redirect(reverse('home'))


def close_channel(request):
    channel = get_object_or_404(Channel, user=request.user)
    user = request.user
    channel_status = check_channel_status(request)
    if channel_status is None:
        return redirect(reverse('my-profile'))
    messages.success(request, 'We have received notification to close your channel. \
        We will be in touch when all due processes are complete')
    send_email(
        "Channel closure request",
        "Admin",
        f"Channel: {channel.name} has requested to be closed",
        settings.ADMIN_EMAIL
    )
    return redirect(reverse('my-profile'))

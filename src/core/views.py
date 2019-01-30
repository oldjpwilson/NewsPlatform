from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404, reverse
from articles.models import Article
from categories.views import get_todays_most_popular_article_categories
from .forms import ChannelCreateForm, ProfileForm, ChannelUpdateForm
from .models import Profile, Channel


def my_profile(request):
    if not request.user.is_authenticated:
        return redirect(reverse('home'))
    profile = get_object_or_404(Profile, user=request.user)
    articles = Article.objects.get_highest_rated(3)
    channels = profile.subscriptions.all()
    sub_count = profile.subscriptions.count()
    context = {
        'profile': profile,
        'article_list': articles,
        'channel_list': channels,
        'sub_count': sub_count,
        'display': 'stats'
    }
    return render(request, 'profile.html', context)


@login_required
def profile_update(request):
    profile = get_object_or_404(Profile, user=request.user)
    form = ProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(reverse('my-profile'))

    context = {
        'display': 'edit_profile',
        'form': form
    }

    return render(request, 'profile.html', context)


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
    return render(request, 'profile.html', context)


@login_required
def profile_update_payment_details(request):
    profile = get_object_or_404(Profile, user=request.user)
    context = {
        'display': 'edit_payment_details',
        'user': request.user,
    }
    return render(request, 'profile.html', context)


@login_required
def my_channel(request):
    if not request.user.is_authenticated:
        return redirect('/')
    channel = get_object_or_404(Channel, user=request.user)
    articles = channel.articles.all()
    context = {
        'channel': channel,
        'articles': articles
    }
    return render(request, 'channel.html', context)


def channel_list(request):
    profile = get_object_or_404(Profile, user=request.user)
    # channels = profile.subscriptions.all()  # only subscribed channels
    channels = Channel.objects.all()

    most_viewed = Article.objects.get_todays_most_viewed_channels(3)
    most_recent = Article.objects.get_todays_most_recent(3)
    most_popular_cats = get_todays_most_popular_article_categories()

    context = {
        'channel_list': channels,
        'most_viewed': most_viewed,
        'most_recent': most_recent,
        'cats': most_popular_cats
    }
    return render(request, 'channel_list.html', context)


@login_required
def channel_public(request, name):
    channel = get_object_or_404(Channel, name=name)
    articles = channel.articles.all().order_by('-published_date')  # TODO: paginate
    context = {
        'channel': channel,
        'articles': articles
    }
    return render(request, 'channel_public.html', context)


@login_required
def channel_create(request):
    if request.user.channel:
        messages.info(request, 'You already are a journalist!')
        return redirect(reverse('my-profile'))

    form = ChannelCreateForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            channel = form.instance
            channel.user = request.user
            channel.save()
            return redirect(reverse('my-profile'))

    context = {
        'form': form,
    }

    return render(request, 'channel_create.html', context)


@login_required
def channel_stats(request):
    if not request.user.channel:
        return redirect(reverse('profile'))
    channel = get_object_or_404(Channel, user=request.user)
    context = {
        'name': channel.name,
        'display': 'stats'
    }
    return render(request, 'channel_update.html', context)


@login_required
def channel_update(request):
    if not request.user.channel:
        return redirect(reverse('profile'))
    channel = get_object_or_404(Channel, user=request.user)
    form = ChannelUpdateForm(request.POST or None, instance=channel)
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
    return render(request, 'channel_update.html', context)


@login_required
def channel_update_payment_details(request):
    channel = get_object_or_404(Channel, user=request.user)
    context = {
        'display': 'edit_payment_details',
    }
    return render(request, 'channel_update.html', context)


@login_required
def subscribe(request, name):
    profile = get_object_or_404(Profile, user=request.user)
    channel = get_object_or_404(Channel, name=name)

    # TODO: if user has no payment details - redirect

    profile.subscriptions.add(channel)
    profile.save()

    channel.subscribers.add(profile)
    channel.save()

    return redirect(channel.get_absolute_url())


@login_required
def unsubscribe(request, name):
    profile = get_object_or_404(Profile, user=request.user)
    channel = get_object_or_404(Channel, name=name)

    profile.subscriptions.remove(channel)
    profile.save()

    channel.subscribers.remove(profile)
    channel.save()

    return redirect(channel.get_absolute_url())

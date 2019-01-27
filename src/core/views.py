from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import Profile, Channel
from articles.models import Article
from .forms import ChannelCreateForm, ProfileForm


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
    articles = channel.article_set.all()
    context = {
        'channel': channel,
        'articles': articles
    }
    return render(request, 'channel.html', context)


def channel_list(request):
    channels = Channel.objects.all()
    context = {
        'channel_list': channels,
    }
    return render(request, 'channel_list.html', context)


def channel_create(request):
    if not request.user.is_authenticated and not request.user.channel:
        messages.info(request, 'You already are a journalist!')
        return redirect(reverse('my-profile'))

    next = request.GET.get('next')
    form = ChannelCreateForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            channel = form.instance
            channel.user = request.user
            channel.save()
            if next:
                return redirect(next)
            return redirect(reverse('my-profile'))

    context = {
        'form': form,
        'button_text': 'Begin!',
        'title': 'Create your channel'
    }

    return render(request, 'channel_update_create.html', context)


def channel_detail(request):
    channel = get_object_or_404(Channel, user=request.user)
    context = {
        'channel': channel
    }
    return render(request, 'channel_detail.html', context)


@login_required
def channel_update(request):
    if not request.user.channel:
        messages.info(
            request, 'Error with your channel. Please contact support.')
        return redirect(reverse('profile'))
    channel = get_object_or_404(Channel, user=request.user)
    form = ChannelCreateForm(request.POST or None, instance=channel)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(reverse('my-channel'))

    context = {
        'form': form,
        'button_text': 'Update',
        'title': 'Update your channel'
    }

    return render(request, 'channel_update_create.html', context)

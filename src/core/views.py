from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404, reverse
from star_ratings.models import Rating
from articles.models import Article, ArticleView
from categories.views import get_todays_most_popular_article_categories
from .forms import ChannelCreateForm, ChannelUpdateForm
from .models import Profile, Channel
from .helpers import paginate_queryset, get_most_viewed_channel


def check_user_is_journalist(user):
    try:
        return user.channel
    except:
        return redirect(reverse('my-profile'))


def check_channel_status(request):
    channel_qs = Channel.objects.filter(user=request.user)
    if not channel_qs.exists():
        return None
    return channel_qs.first()


@login_required
def my_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    articles = Article.objects.get_highest_rated(3)
    queryset, page_request_var = paginate_queryset(request, articles)
    channels = profile.subscriptions.all()
    sub_count = profile.subscriptions.count()
    total_article_views = ArticleView.objects.filter(user=request.user).count()
    most_viewed_channel = get_most_viewed_channel(request.user)
    context = {
        'profile': profile,
        'queryset': queryset,
        'channel_list': channels,
        'sub_count': sub_count,
        'total_article_views': total_article_views,
        'most_viewed_channel': most_viewed_channel,
        'display': 'stats',
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
    context = {
        'display': 'edit_payment_details',
        'user': request.user,
    }
    return render(request, 'core/profile.html', context)


@login_required
@user_passes_test(check_user_is_journalist)
def my_channel(request):
    channel = get_object_or_404(Channel, user=request.user)
    articles = channel.articles.all().order_by('-published_date')
    highest_rated_article = channel.articles.all().order_by('-rating')[0]
    most_viewed_article = channel.articles.all().order_by('-view_count')[0]
    queryset, page_request_var = paginate_queryset(request, articles)
    context = {
        'channel': channel,
        'queryset': queryset,
        'highest_rated_article': highest_rated_article,
        'most_viewed_article': most_viewed_article,
        'page_request_var': page_request_var
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
            channel = form.instance
            channel.user = request.user
            channel.save()
            return redirect(reverse('my-profile'))
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
    return render(request, 'core/channel_update.html', context)


@login_required
@user_passes_test(check_user_is_journalist)
def channel_update_payment_details(request):
    channel = get_object_or_404(Channel, user=request.user)
    context = {
        'name': channel.name,
        'display': 'edit_payment_details',
    }
    return render(request, 'core/channel_update.html', context)


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

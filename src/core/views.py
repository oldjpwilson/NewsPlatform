from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Channel
from articles.models import Article
from .forms import ChannelCreateForm


def my_profile_view(request):
    if not request.user.is_authenticated:
        return redirect('/')
    profile = get_object_or_404(Profile, user=request.user)
    articles = Article.objects.get_highest_rated(3)
    channels = profile.subscriptions.all()
    sub_count = profile.subscriptions.count()
    context = {
        'profile': profile,
        'article_list': articles,
        'channel_list': channels,
        'sub_count': sub_count
    }
    return render(request, 'profile.html', context)


def my_channel_view(request):
    if not request.user.is_authenticated:
        return redirect('/')
    channel = get_object_or_404(Channel, user=request.user)
    context = {
        'channel': channel,
    }
    return render(request, 'channel.html', context)


def channel_list(request):
    channels = Channel.objects.all()
    context = {
        'channel_list': channels,
    }
    return render(request, 'channel_list.html', context)


def channel_create(request):
    print(request.user.channel)
    if not request.user.is_authenticated and request.user.channel:
        # TODO: add messages framework
        return redirect('/profile/')

    next = request.GET.get('next')
    form = ChannelCreateForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            channel = form.instance
            channel.user = request.user
            channel.save()
            if next:
                return redirect(next)
            return redirect('/profile')

    context = {
        'form': form
    }

    return render(request, 'channel_create.html', context)


def channel_detail(request):
    channel = get_object_or_404(Channel, user=request.user)
    context = {
        'channel': channel
    }
    return render(request, 'channel_detail.html', context)


def channel_update(request):
    if not request.user.is_authenticated and not request.user.channel:
        # TODO: add messages framework
        return redirect('/profile/')
    channel = get_object_or_404(Channel, user=request.user)
    form = ChannelCreateForm(request.POST or None, instance=channel)
    if request.method == 'POST':
        if form.is_valid():
            channel = form.instance
            channel.user = request.user
            channel.save()
            return redirect('/profile/')

    context = {
        'form': form
    }

    return render(request, 'channel_create.html', context)

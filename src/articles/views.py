from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from core.forms import LoginForm
from core.models import Channel
from .forms import ArticleModelForm
from .models import Article


def home(request):
    if request.user.is_authenticated:
        return redirect('/articles/')
    articles = Article.objects.get_highest_rated(3)
    channels = Channel.objects.get_highest_rated(3)

    # handle post request for logging in
    next = request.GET.get('next')
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            if next:
                return redirect(next)
            return redirect('/')

    context = {
        'article_list': articles,
        'channel_list': channels,
        'form': form
    }
    return render(request, 'home.html', context)


def article_list(request):
    articles = Article.objects.all()
    context = {
        'article_list': articles
    }
    return render(request, 'article_list.html', context)


def article_detail(request, id):
    article = get_object_or_404(Article, id=id)
    article.view_count = article.view_count + 1
    article.save()  # TODO: make this better
    context = {
        'article': article
    }
    return render(request, 'article_detail.html', context)


def article_create(request):
    form = ArticleModelForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            channel = Channel.objects.get(user__username='admin')
            form.instance.channel = channel
            form.save()
            return redirect(reverse('articles:detail', kwargs={
                'id': form.instance.id
            }))
    context = {
        'form': form
    }
    return render(request, 'article_create.html', context)


def article_update(request, id):
    instance = get_object_or_404(Article, id=id)
    form = ArticleModelForm(request.POST or None,
                            request.FILES or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(reverse('articles:detail', kwargs={
                'id': form.instance.id
            }))
    context = {
        'form': form
    }
    return render(request, 'article_create.html', context)


def article_delete(request, id):
    article = get_object_or_404(Article, id=id)
    article.delete()
    return redirect('/')

from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from core.models import Channel
from .forms import ArticleModelForm
from .models import Article


def home(request):
    articles = Article.objects.get_highest_rated(3)
    channels = Channel.objects.get_highest_rated(3)

    # handle post request for logging in

    context = {
        'article_list': articles,
        'channel_list': channels
    }
    return render(request, 'home.html', context)


def list_view(request):
    articles = Article.objects.all()
    context = {
        'article_list': articles
    }
    return render(request, 'article_list.html', context)


def detail_view(request, id):
    article = get_object_or_404(Article, id=id)
    context = {
        'article': article
    }
    return render(request, 'article_detail.html', context)


def create_view(request):
    form = ArticleModelForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            print(form.instance)
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

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from core.forms import LoginForm
from core.models import Channel
from .forms import ArticleFilterForm, ArticleModelForm, ContactForm
from .models import Article


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            messages.info(
                request, 'Thanks for contacting us. We\'ll get back to you as soon as possible!')
            form_email = form.cleaned_data['email']
            form_message = form.cleaned_data['message']
            form_full_name = form.cleaned_data['name']
            subject = 'Message from Justdjango contact form'
            from_email = settings.EMAIL_HOST_USER
            to_email = ['admin@justdjango.com']
            contact_message = "%s: %s via %s" % (
                form_full_name,
                form_message,
                form_email)
            send_mail(subject,
                      contact_message,
                      from_email,
                      to_email,
                      fail_silently=True)
            return redirect(reverse('article-list'))

    context = {
        'form': form
    }

    return render(request, "contact.html", context)


def home(request):
    if request.user.is_authenticated:
        return redirect(reverse('article-list'))
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
    queryset = Article.objects.all()
    most_viewed = Article.objects.get_todays_most_viewed(3)
    most_recent = Article.objects.get_todays_most_recent(3)

    form = ArticleFilterForm(request.GET or None)
    if form.is_valid():
        latest = form.cleaned_data.get('latest')
        if latest:
            queryset = queryset.order_by('-published_date')
        view_count = form.cleaned_data.get('view_count')
        if view_count:
            queryset = queryset.order_by('-view_count')
        rating = form.cleaned_data.get('rating')
        if rating:
            queryset = queryset.order_by('-rating')

    context = {
        'article_list': queryset,
        'most_viewed': most_viewed,
        'most_recent': most_recent,
        'form': form
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

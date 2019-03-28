from django.db.models import Q
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from core.forms import LoginForm
from core.helpers import paginate_queryset, get_remaining_free_views, get_channel_from_session
from core.models import Channel, Profile
from core.views import check_user_is_journalist, check_channel_has_stripe_account, is_article_creator
from categories.models import Category
from categories.views import get_todays_most_popular_article_categories
from .filters import ArticleFilter
from .forms import ArticleFilterForm, ArticleModelForm, ContactForm
from .models import Article, ArticleView, FreeView


def search(request):
    articles = Article.objects.all()
    channels = Channel.objects.all()
    query = request.GET.get('q')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(content__icontains=query)
        ).distinct()

        channels = channels.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    context = {
        'articles': articles,
        'channels': channels
    }
    return render(request, 'articles/search_results.html', context)


def about(request):
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
        'form': form
    }
    return render(request, 'nav/about.html', context)


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            messages.info(
                request, 'Thanks for contacting us. We\'ll get back to you as soon as possible!')
            form_email = form.cleaned_data['email']
            form_message = form.cleaned_data['message']
            form_full_name = form.cleaned_data['name']
            subject = 'Message from NewsPlatform contact form'
            from_email = settings.EMAIL_HOST_USER
            to_email = [settings.ADMIN_EMAIL]  # we send it to ourselves
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

    return render(request, "nav/contact.html", context)


def home(request):
    if request.user.is_authenticated:
        return redirect(reverse('article-list'))
    articles = Article.objects.get_highest_rated(3)
    channels = Channel.objects.get_highest_rated(3)
    categories = Category.objects.all()

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
        'categories': categories,
        'form': form
    }
    return render(request, 'nav/home.html', context)


@login_required
def article_list(request):
    profile = get_object_or_404(Profile, user=request.user)
    subscriptions = profile.subscriptions.all()
    articles = Article.objects.all()
    most_viewed = Article.objects.get_todays_most_viewed(3)
    most_recent = Article.objects.get_todays_most_recent(3)
    most_popular_cats = get_todays_most_popular_article_categories()

    form = ArticleFilterForm(request.GET or None)
    if form.is_valid():
        latest = form.cleaned_data.get('latest')
        if latest:
            articles = articles.order_by('-published_date')
        view_count = form.cleaned_data.get('view_count')
        if view_count:
            articles = articles.order_by('-view_count')
        rating = form.cleaned_data.get('rating')
        if rating:
            articles = articles.order_by('-rating__average')

    # let user see only articles of subscribed channels
    final_articles = [a for a in articles if a.channel in subscriptions]
    queryset, page_request_var = paginate_queryset(request, final_articles, 4)

    context = {
        'queryset': queryset,
        'page_request_var': page_request_var,
        'most_viewed': most_viewed,
        'most_recent': most_recent,
        'cats': most_popular_cats,
        'form': form
    }
    return render(request, 'articles/article_list.html', context)


def article_explore(request):
    articles = Article.objects.all()
    filtered_articles = ArticleFilter(request, articles)
    queryset, page_request_var = paginate_queryset(
        request, filtered_articles, 12)
    most_viewed = Article.objects.get_todays_most_viewed_channels(3)
    most_recent = Article.objects.get_todays_most_recent(3)
    most_popular_cats = get_todays_most_popular_article_categories()
    context = {
        'queryset': queryset,
        'page_request_var': page_request_var,
        'most_viewed': most_viewed,
        'most_recent': most_recent,
        'cats': most_popular_cats,
        'categories': Category.objects.all()
    }
    return render(request, 'articles/article_explore.html', context)


@login_required
def article_detail(request, id):
    most_viewed = Article.objects.get_todays_most_viewed(3)
    most_recent = Article.objects.get_todays_most_recent(3)
    most_popular_cats = get_todays_most_popular_article_categories()
    article = get_object_or_404(Article, id=id)

    # handle if the visitor is subscribed
    profile = get_object_or_404(Profile, user=request.user)
    subscribed = False
    RFV = 0

    if is_article_creator(request, article) is False:
        article_view, created = ArticleView.objects.get_or_create(
            article=article,
            user=request.user
        )
        article.view_count = article.view_count + 1
        article.save()

    if profile in article.channel.subscribers.all():
        subscribed = True
        if is_article_creator(request, article) is False:
            if created:
                article.view_count = article.view_count + 1
                article.save()
    else:
        RFV = get_remaining_free_views(request.user, article.channel)
        # create a new free view only if user is not the creator
        if is_article_creator(request, article) is False:
            FreeView.objects.get_or_create(
                user=request.user,
                channel=article.channel,
                article_view=article_view
            )

    if is_article_creator(request, article) is False and subscribed is False:
        if RFV > 0:
            messages.info(
                request, f"You have {RFV} free views left for this channel")

    allowed_to_view = False
    if subscribed is True or RFV > 0:
        allowed_to_view = True

    context = {
        'article': article,
        'most_viewed': most_viewed,
        'most_recent': most_recent,
        'cats': most_popular_cats,
        'allowed_to_view': allowed_to_view
    }
    return render(request, 'articles/article_detail.html', context)


@login_required
@user_passes_test(check_user_is_journalist)
def article_create(request):
    channel_name = get_channel_from_session(request)
    channel = Channel.objects.get(user=request.user, name=channel_name)
    form = ArticleModelForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            article = form.save(commit=False)
            article.channel = channel
            article.save()
            form.save_m2m()
            return redirect(reverse('article-detail', kwargs={
                'id': form.instance.id
            }))
    context = {
        'form': form
    }
    return render(request, 'articles/article_create.html', context)


@login_required
@user_passes_test(check_user_is_journalist)
def article_update(request, id):
    instance = get_object_or_404(Article, id=id)
    form = ArticleModelForm(request.POST or None,
                            request.FILES or None,
                            instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(reverse('article-detail', kwargs={
                'id': form.instance.id
            }))
    context = {
        'form': form
    }
    return render(request, 'articles/article_create.html', context)


@login_required
@user_passes_test(check_user_is_journalist)
def article_delete(request, id):
    article = get_object_or_404(Article, id=id)
    article.delete()
    return redirect(reverse('home'))

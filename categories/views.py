from django.db.models import Count, Sum
from django.shortcuts import render
from articles.models import Article
from core.helpers import paginate_queryset
from core.models import Channel
from .models import Category


def get_todays_most_popular_article_categories():
    todays_cats = Article.objects \
        .get_todays() \
        .values('categories__name') \
        .annotate(cat_count=Count('categories__name')) \
        .order_by('cat_count')[:3]
    return todays_cats


def category_detail(request, name):
    most_viewed = Article.objects.get_todays_most_viewed_channels(3)
    most_recent = Article.objects.get_todays_most_recent(3)
    most_popular_cats = get_todays_most_popular_article_categories()
    articles = Category.objects.get(name=name) \
        .article_set \
        .distinct() \
        .order_by('-published_date')
    queryset, page_request_var = paginate_queryset(request, articles, 12)
    context = {
        'queryset': queryset,
        'page_request_var': page_request_var,
        'most_viewed': most_viewed,
        'most_recent': most_recent,
        'cats': most_popular_cats
    }
    return render(request, "categories/category_detail.html", context)

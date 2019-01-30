from django.db.models import Count, Sum
from articles.models import Article
from core.models import Channel


def get_todays_most_popular_article_categories():
    todays_cats = Article.objects \
        .get_todays() \
        .values('categories__name') \
        .annotate(cat_count=Count('categories__name')) \
        .order_by('cat_count')[:3]
    return todays_cats

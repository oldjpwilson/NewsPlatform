from django.db.models import Count
from articles.models import Article


def get_todays_most_popular_categories():
    todays_cats = Article.objects \
        .get_todays() \
        .values('categories__name') \
        .annotate(cat_count=Count('categories__name'))
    return todays_cats

from datetime import datetime
from django.db.models import Sum
from .models import Article


def formattedDate(d):
    date = datetime.strftime(d, '%Y-%m-%d')
    return datetime.strptime(date, "%Y-%m-%d")


def articleObj(a):
    return {
        "view_count": a.get_view_count(),
        "title": a.title,
        "publish_date": a.published_date,
        "rating": a.get_rating,
        "get_absolute_url": a.get_absolute_url(),
        "categories": [cat.name for cat in a.categories.all()]
    }


def ArticleFilter(request, queryset):
    article_title = request.GET.get('article_title')
    publishDateMin = request.GET.get('publishDateMin')
    publishDateMax = request.GET.get('publishDateMax')
    ratingMin = request.GET.get('ratingMin')
    ratingMax = request.GET.get('ratingMax')
    viewCountMin = request.GET.get('viewCountMin')
    viewCountMax = request.GET.get('viewCountMax')
    order_by_publish_date = request.GET.get('publish_date')
    order_by_rating = request.GET.get('rating')
    order_by_view_count = request.GET.get('view_count')
    categories = request.GET.getlist('categories')

    # start with all articles and manipulate the queryset depending on form input
    qs = Article.objects.all()

    # check if article title was searched
    if article_title != '' and article_title is not None:
        qs = qs.filter(title__icontains=article_title)
        qs = [articleObj(c) for c in qs]
    else:
        qs = [articleObj(c) for c in qs]

        # then check if any of the checkboxes for ordering were selected
        if order_by_publish_date == 'on':
            qs = sorted(
                qs, key=lambda i: i['publish_date'], reverse=True)

        elif order_by_rating == 'on':
            qs = [a for a in qs if a['rating'] is not None]
            qs = sorted(
                qs, key=lambda i: i['rating'].average, reverse=True)

        elif order_by_view_count == 'on':
            qs = sorted(qs, key=lambda i: i['view_count'], reverse=True)

        # then check if any of the inputs were used

        if publishDateMin != '' and publishDateMin is not None:
            qs = [a for a in qs if formattedDate(
                a.get("publish_date")) > datetime.strptime(publishDateMin, "%Y-%m-%d")]

        if publishDateMax != '' and publishDateMax is not None:
            qs = [a for a in qs if formattedDate(
                a.get("publish_date")) < datetime.strptime(publishDateMax, "%Y-%m-%d")]

        if ratingMin != '' and ratingMin is not None:
            qs = [a for a in qs if a['rating'] is not None]
            qs = [a for a in qs if a['rating'].count > 0]
            qs = [a for a in qs if a['rating'].average > int(ratingMin)]

        if ratingMax != '' and ratingMax is not None:
            qs = [a for a in qs if a['rating'] is not None]
            qs = [a for a in qs if a['rating'].count > 0]
            qs = [a for a in qs if a['rating'].average < int(ratingMax)]

        if viewCountMin != '' and viewCountMin is not None:
            qs = [a for a in qs if a['view_count'] > int(viewCountMin)]

        if viewCountMax != '' and viewCountMax is not None:
            qs = [a for a in qs if a['view_count'] < int(viewCountMax)]

    # if there were categories selected
    if len(categories) > 0:
        for cat in categories:
            qs = [a for a in qs if cat in a['categories']]

    return qs

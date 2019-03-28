from django.db.models import Q, Sum
from .models import Channel


def channelObj(c):
    return {
        "view_count": c.view_count if c.view_count is not None else 0,
        "name": c.name,
        "subscriber_count": c.subscriber_count,
        "article_count": c.article_count,
        "channel_rating": c.channel_rating if c.channel_rating is not None else -1,
        "get_absolute_url": c.get_absolute_url(),
        "categories": [cat.name for cat in c.categories.all()],
        "description": c.description
    }


def ChannelFilter(request, queryset):
    channel_name = request.GET.get('channel_name')
    subCountMin = request.GET.get('subCountMin')
    subCountMax = request.GET.get('subCountMax')
    articleCountMin = request.GET.get('articleCountMin')
    articleCountMax = request.GET.get('articleCountMax')
    viewCountMin = request.GET.get('viewCountMin')
    viewCountMax = request.GET.get('viewCountMax')
    order_by_article_count = request.GET.get('article_count')
    order_by_rating = request.GET.get('rating')
    order_by_sub_count = request.GET.get('sub_count')
    order_by_alphabetical = request.GET.get('alphabetical')
    categories = request.GET.getlist('categories')

    # start with all channels and manipulate the queryset depending on form input
    qs = Channel.objects.all()

    # check if channel name was searched
    if channel_name != '' and channel_name is not None:
        qs = qs.filter(
            Q(name__icontains=channel_name)
        ).distinct()

    # then check if any of the checkboxes for ordering were selected
    elif order_by_article_count == 'on':
        channels = [channelObj(c) for c in qs]
        qs = sorted(channels, key=lambda i: i['article_count'], reverse=True)
    elif order_by_sub_count == 'on':
        channels = [channelObj(c) for c in qs]
        qs = sorted(
            channels, key=lambda i: i['subscriber_count'], reverse=True)
    elif order_by_rating == 'on':
        channels = [channelObj(c) for c in qs]
        qs = sorted(
            channels, key=lambda i: i['channel_rating'], reverse=True)
    elif order_by_alphabetical == 'on':
        channels = [channelObj(c) for c in qs]
        qs = sorted(channels, key=lambda i: i['name'])

    # then check if any of the inputs were used
    if subCountMin != '' and subCountMin is not None:
        qs = [c for c in qs if c.subscriber_count > int(subCountMin)]

    if subCountMax != '' and subCountMax is not None:
        qs = [c for c in qs if c.subscriber_count < int(subCountMax)]

    if articleCountMin != '' and articleCountMin is not None:
        qs = [c for c in qs if c.article_count > int(articleCountMin)]

    if articleCountMax != '' and articleCountMax is not None:
        qs = [c for c in qs if c.article_count < int(articleCountMax)]

    if viewCountMin != '' and viewCountMin is not None:
        qs = [c for c in qs if c.view_count is not None]
        qs = [c for c in qs if c.view_count > int(viewCountMin)]

    if viewCountMax != '' and viewCountMax is not None:
        qs = [c for c in qs if c.view_count is not None]
        qs = [c for c in qs if c.view_count < int(viewCountMax)]

    # if there were categories selected
    if len(categories) > 0:
        for cat in categories:
            qs = [channelObj(c) for c in qs]
            qs = [c for c in qs if cat in c['categories']]

    return qs

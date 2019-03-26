from django.db.models import Q, Sum
from .models import Channel


def channelObj(c):
    return {
        "view_count": c.view_count if c.view_count is not None else 0,
        "name": c.name,
        "subscriber_count": c.subscriber_count,
        "article_count": c.article_count,
        "channel_rating": c.channel_rating if c.channel_rating is not None else -1,
        "get_absolute_url": c.get_absolute_url()
    }


def ChannelFilter(request, queryset):
    channel_name = request.GET.get('channel_name')
    subCountMin = request.GET.get('subCountMin')
    subCountMax = request.GET.get('subCountMax')
    articleCountMin = request.GET.get('articleCountMin')
    articleCountMax = request.GET.get('articleCountMax')
    viewCountMin = request.GET.get('viewCountMin')
    viewCountMax = request.GET.get('viewCountMax')
    order_by_view_count = request.GET.get('view_count')
    order_by_rating = request.GET.get('rating')
    order_by_sub_count = request.GET.get('sub_count')

    qs = Channel.objects.all()

    # first check if rating, view_count or channel name were searched
    if channel_name != '' and channel_name is not None:
        qs = qs.filter(
            Q(name__iexact=channel_name)
        ).distinct()
    elif order_by_view_count == 'on':
        channels = [channelObj(c) for c in qs]
        qs = sorted(channels, key=lambda i: i['view_count'], reverse=True)
    elif order_by_sub_count == 'on':
        channels = [channelObj(c) for c in qs]
        qs = sorted(
            channels, key=lambda i: i['subscriber_count'], reverse=True)
    elif order_by_rating == 'on':
        channels = [channelObj(c) for c in qs]
        qs = sorted(
            channels, key=lambda i: i['channel_rating'], reverse=True)

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

    return qs

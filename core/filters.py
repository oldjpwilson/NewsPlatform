from .models import Channel


def ChannelFilter(request, queryset):
    print(request.GET)
    # filter the channel object based on the request.GET parameters
    return queryset

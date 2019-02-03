from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from articles.models import ArticleView


def paginate_queryset(request, queryset):
    paginator = Paginator(queryset, 4)
    page_request_var = 'page'
    page = request.GET.get('page')
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)
    return paginated_queryset, page_request_var


def get_most_viewed_channel(user):
    views = ArticleView \
        .objects \
        .filter(user=user) \
        .values('article__channel__name') \
        .annotate(count=Count('article__channel__name')) \
        .order_by('count')[0]
    return views

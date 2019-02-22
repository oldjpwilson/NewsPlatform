from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from articles.models import ArticleView
from core.models import Channel


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
    views_qs = ArticleView \
        .objects \
        .filter(user=user) \
        .values('article__channel__name') \
        .annotate(count=Count('article__channel__name')) \
        .order_by('count')
    if views_qs.exists():
        return views_qs[0]
    return None


def get_highest_rated_article(channel):
    qs = channel.articles.all()
    if qs.exists():
        return qs.order_by('-rating')[0]
    return None


def get_most_viewed_article(channel):
    qs = channel.articles.all()
    if qs.exists():
        return qs.order_by('-view_count')[0]
    return None


def send_email(subject, full_name, message, email):
    from_email = settings.EMAIL_HOST_USER
    to_email = [email]
    contact_message = "%s: %s via %s" % (
        full_name,
        message,
        email
    )
    send_mail(subject,
              contact_message,
              from_email,
              to_email,
              fail_silently=True)

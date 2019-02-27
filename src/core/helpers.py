from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from articles.models import ArticleView
from core.models import Channel, Subscription


def get_dates():
    first_day_of_current_month = datetime.now().replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
    return (first_day_of_current_month, first_day_of_previous_month)


def get_channel_current_billing_revenue(channel):
    # get subscriptions created in previous month
    dates = get_dates()
    new_subscriptions = Subscription.objects \
        .filter(
            channel=channel,
            modified_at__range=[dates[1], dates[0]]
        )
    return 0.5 * new_subscriptions.count()


def get_channel_alltime_billing_revenue(channel):
    dates = get_dates()
    amount = 0
    # get all subscriptions that started before 1 month ago
    # - but only the ones that are still subscribed
    recurring_subscriptions = Subscription.objects \
        .filter(
            channel=channel,
            modified_at__lte=dates[1]
        ).exclude(active=False)
    # get subscriptions created in previous month
    new_subscriptions = Subscription.objects \
        .filter(
            channel=channel,
            modified_at__range=[dates[1], dates[0]]
        )
    # update total amount to pay journalist
    amount += 0.5 * (recurring_subscriptions.count() +
                     new_subscriptions.count())
    return amount


def get_profile_current_billing_total(profile):
    dates = get_dates()
    # get subscriptions created in previous month
    new_subscriptions = Subscription.objects \
        .filter(
            profile=profile,
            modified_at__range=[
                dates[1], dates[0]]
        )
    return 0.5 * new_subscriptions.count()


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

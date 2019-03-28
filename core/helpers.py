import datetime
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from articles.models import ArticleView, FreeView
from core.models import Channel, Subscription, Payout


def get_channel_from_session(request):
    user_channels = Channel.objects.filter(user=request.user)
    try:
        channel_name = request.session['selected_channel']
    except KeyError:
        channel_name = user_channels[0].name
        request.session['selected_channel'] = channel_name
    channel = get_object_or_404(Channel, name=channel_name)
    return channel


def get_channel_or_404(request, name=None):
    if name is None:
        return get_channel_from_session(request)
    else:
        return get_object_or_404(Channel, name=name)


def get_dates():
    first_day_of_current_month = datetime.datetime.now().replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
    return (first_day_of_current_month, first_day_of_previous_month)


def get_channel_current_billing_revenue(channel):
    # get subscriptions created in previous month
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
    amount += 0.25 * (recurring_subscriptions.count() +
                      new_subscriptions.count())
    return amount


def get_channel_alltime_billing_revenue(channel):
    channel_payouts = Payout.objects \
        .filter(channel=channel) \
        .exclude(success=False) \
        .values('amount') \
        .annotate(total=Sum('amount'))
    if channel_payouts.exists():
        return channel_payouts[0]['total']
    return 0.0


def get_previous_pay_date(curr_date):
    new_month = curr_date.month - 1
    new_year = curr_date.year
    if curr_date.month == 1:
        new_month = 12
        new_year = curr_date.year - 1
    return datetime.date(new_year, new_month, 26)


def get_next_date(day):
    curr_date = datetime.date.today()
    if curr_date.day >= day:
        new_month = curr_date.month + 1
        new_year = curr_date.year
        if curr_date.month == 12:
            new_month = 1
            new_year = curr_date.year + 1
        return datetime.date(new_year, new_month, day)
    return datetime.date(curr_date.year, curr_date.month, day)


def get_profile_current_billing_total(profile):
    today_date = datetime.date.today()
    today_date_midnight = datetime.date(
        today_date.year, today_date.month, today_date.day + 1)
    previous_pay_date = get_previous_pay_date(today_date)
    amount = 0
    # get all subscriptions that started before 1 month ago
    # - but only the ones that are still subscribed
    recurring_subscriptions = Subscription.objects \
        .filter(
            profile=profile,
            modified_at__lte=previous_pay_date
        ).exclude(active=False)
    # get subscriptions created in previous month
    new_subscriptions = Subscription.objects \
        .filter(
            profile=profile,
            modified_at__range=[previous_pay_date, today_date_midnight]
        )
    amount += 0.5 * (recurring_subscriptions.count() +
                     new_subscriptions.count())
    return amount


def paginate_queryset(request, queryset, count=4):
    paginator = Paginator(queryset, count)
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


def get_remaining_free_views(user, channel):
    free_view_count = FreeView.objects \
        .filter(user=user, channel=channel) \
        .count()
    return int(settings.NUM_FREE_VIEWS_PER_CHANNEL) - free_view_count

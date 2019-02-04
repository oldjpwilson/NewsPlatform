from datetime import datetime, timedelta
from django.db import models
from django.db.models import Count, Sum
from core.models import Channel

RATING = 'rating'
VIEW_COUNT = 'view_count'
RECENT = 'published_date'


class ArticleQuerySet(models.QuerySet):

    def get_highest(self, field, count):
        return self.order_by(f'-{field}')[:count]

    def get_highest_rating(self, count):
        return self.objects.filter(ratings__isnull=False).order_by('ratings__average')[:count]

    def get_before_time(self, hours):
        time_threshold = datetime.now() - timedelta(hours=hours)
        return time_threshold

    def get_todays(self):
        time_threshold = self.get_before_time(24)
        return self.filter(published_date__gt=time_threshold)

    def get_todays_most_viewed(self, field, count):
        return self.get_todays().order_by(f'-{field}')[:count]

    def get_todays_most_recent(self, field, count):
        return self.get_todays().order_by(f'-{field}')[:count]

    def get_todays_most_viewed_channels(self, count):
        return self.get_todays().values('channel__name').annotate(Sum('view_count')).order_by()[0:count]


class ArticleManager(models.Manager):

    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset()

    def get_highest_rated(self, count):
        return self.get_queryset().get_highest_rating(count)

    def get_todays(self):
        return self.get_queryset().get_todays()

    def get_todays_most_viewed(self, count):
        return self.get_queryset().get_todays_most_viewed(VIEW_COUNT, count)

    def get_todays_most_recent(self, count):
        return self.get_queryset().get_todays_most_recent(RECENT, count)

    def get_todays_most_viewed_channels(self, count):
        return self.get_queryset().get_todays_most_viewed_channels(count)

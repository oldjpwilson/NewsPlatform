from datetime import datetime, timedelta
from django.db import models

RATING = 'rating'
VIEW_COUNT = 'view_count'
RECENT = 'published_date'


class ArticleQuerySet(models.QuerySet):

    def get_highest(self, field, count):
        return self.order_by(f'-{field}')[0:count]

    def get_before_time(self, hours):
        time_threshold = datetime.now() - timedelta(hours=hours)
        return time_threshold

    def get_todays_most_viewed(self, field, count):
        time_threshold = self.get_before_time(24)
        return self.filter(published_date__gt=time_threshold).order_by(f'-{field}')[0:count]

    def get_todays_most_recent(self, field, count):
        time_threshold = self.get_before_time(24)
        return self.filter(published_date__gt=time_threshold).order_by(f'-{field}')[0:count]


class ArticleManager(models.Manager):

    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset()

    def get_highest_rated(self, count):
        return self.get_queryset().get_highest(RATING, count)

    def get_todays_most_viewed(self, count):
        return self.get_queryset().get_todays_most_viewed(VIEW_COUNT, count)

    def get_todays_most_recent(self, count):
        return self.get_queryset().get_todays_most_recent(RECENT, count)

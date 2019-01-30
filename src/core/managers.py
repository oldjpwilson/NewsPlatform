from django.db import models

RATING = 'rating'
VIEW_COUNT = 'view_count'


class ChannelQuerySet(models.QuerySet):

    def get_highest(self, field, count):
        return self.order_by(field)[0:count]

    def get_todays(self):
        time_threshold = self.get_before_time(24)
        return self.filter(published_date__gt=time_threshold)


class ChannelManager(models.Manager):

    def get_queryset(self):
        return ChannelQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset()

    def get_highest_rated(self, count):
        return self.get_queryset().get_highest(RATING, count)

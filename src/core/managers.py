from django.db import models

RATING = 'rating'


class ChannelQuerySet(models.QuerySet):

    def get_highest(self, field, count):
        return self.order_by(field)[0:count]


class ChannelManager(models.Manager):

    def get_queryset(self):
        return ChannelQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset()

    def get_highest_rated(self, count):
        return self.get_queryset().get_highest(RATING, count)

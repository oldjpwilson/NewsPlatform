from django.db import models

RATING = 'rating'
VIEW_COUNT = 'view_count'


class ArticleQuerySet(models.QuerySet):

    def get_highest(self, field, count):
        return self.order_by(field)[0:count]


class ArticleManager(models.Manager):

    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset()

    def get_highest_rated(self, count):
        return self.get_queryset().get_highest(RATING, count)

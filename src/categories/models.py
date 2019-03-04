from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    @property
    def get_absolute_url(self):
        return reverse('category-detail', kwargs={
            'name': self.name
        })

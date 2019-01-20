from django.db import models

'''
Sport
Tech
Lifestyle
Entertainment
Historical
Political
Religious
Humour
Arts
Education
'''


class Category(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()

    def __str__(self):
        return self.name

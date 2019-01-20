import datetime
import random
import django
import os
from articles.models import Article
from categories.models import Category

os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "newsPlatform.settings.development")
django.setup()

titles = {
    1: 'This is the first example',
    2: 'How about another one?',
    3: 'Just for fun'
}

descriptions = {
    1: 'blah fhiwfiew fwief w fjwkfjk f',
    2: 'dqijdshfk sfhjhfwehf ewjfhewjf jewk f',
    3: 'dfjekj fejwfhew fjwef ewj fwjn skf'
}

media_types = {
    1: 'article',
    2: 'picture',
    3: 'video'
}

contents = {
    1: 'Does this work?',
    2: 'How about this',
    3: 'Testing 123'
}

ratings = {
    1: 1,
    2: 2,
    3: 3
}

categories = {
    1: Category.objects.get(name='Sport'),
    2: Category.objects.get(name='Tech'),
    3: Category.objects.get(name='Lifestyle')
}


def get_create_categories():
    Category.objects.get_or_create(name='Sport')
    Category.objects.get_or_create(name='Tech')
    Category.objects.get_or_create(name='Lifestyle')


def generate():
    get_create_categories()
    for i in range(100):
        a = Article()
        a.title = titles[random.randint(1, 3)]
        a.description = descriptions[random.randint(1, 3)]
        a.media_type = media_types[random.randint(1, 3)]
        # a.content = contents[random.randint(1, 3)]
        a.rating = ratings[random.randint(1, 3)]
        a.save()

        a.categories.add(categories[random.randint(1, 3)])

from django.core.management.base import BaseCommand
from articles.models import Duration, Urgency
from categories.models import Category

names = [
    'Sport',
    'Tech',
    'Lifestyle',
    'Entertainment',
    'Motoring',
    'Political',
    'Science',
    'Business',
    'Health',
    'Environment'
]

durations = [
    'Blitz (under 5 min)',
    'Normal Bulletin (5-15 min) ',
    'Expose/ Longform/ Documentary (Over 15min)'
]

urgencies = [
    'Breaking News (last hour)',
    'Breaking News Updates',
    'Normal News',
    'Interest/ Documentary (not urgent) '
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for name in names:
            category = Category.objects.get_or_create(name=name)
        for duration in durations:
            duration = Duration.objects.get_or_create(type=duration)
        for urgency in urgencies:
            duration = Urgency.objects.get_or_create(type=urgency)

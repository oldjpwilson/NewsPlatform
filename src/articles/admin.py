from django.contrib import admin
from .models import Article, ArticleView, Duration, Urgency
from star_ratings.models import Rating


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'channel', 'rating_average', 'rating_count')
    readonly_fields = ('rating_average', 'rating_count')
    list_display_links = ('title', 'channel')
    list_filter = ('media_type', 'urgency', 'duration')
    search_fields = ('title', 'channel')
    fieldsets = (
        (None, {
            'fields': (
                'channel',
                'title',
                'description',
                'thumbnail',
                'media_type',
                'categories',
                'urgency',
                'duration',
                'content',
                'draft'
            )
        }),
    )

    def rating_average(self, obj):
        rating = Rating.objects.get(object_id=obj.id)
        return rating.average

    def rating_count(self, obj):
        rating = Rating.objects.get(object_id=obj.id)
        return rating.count


admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleView)
admin.site.register(Duration)
admin.site.register(Urgency)

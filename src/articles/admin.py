from django.contrib import admin
from .models import Article


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'channel')
    list_display_links = ('title', 'channel')
    list_filter = ('title', 'channel', 'media_type', 'urgency',
                   'duration',
                   'rating')
    search_fields = ('title', 'channel')
    fieldsets = (
        (None, {
            'fields': (
                'channel',
                'title',
                'description',
                'media_type',
                'categories',
                'urgency',
                'duration',
                'content',
                'rating'
            )
        }),
    )


admin.site.register(Article, ArticleAdmin)

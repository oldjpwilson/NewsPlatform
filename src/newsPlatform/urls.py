from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from articles.views import (
    contact,
    home,
    article_list,
    article_detail,
    article_create,
    article_update,
    article_delete
)

from core.views import (
    my_profile,
    my_channel,
    channel_list,
    channel_detail,
    channel_create,
    channel_update
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # home view
    path('', home, name='home'),
    path('contact/', contact, name='contact'),

    # article views
    path('news-feed/', article_list, name='article-list'),
    path('articles/<id>/', article_detail, name='article-detail'),
    path('create/', article_create, name='article-create'),
    path('articles/<id>/update/', article_update, name='article-update'),
    path('articles/<id>/delete/', article_delete, name='article-delete'),

    # channel views
    path('explore/', channel_list, name='channel-list'),
    path('channels/<name>/', channel_detail, name='channel-detail'),
    path('become-a-journalist/', channel_create, name='channel-create'),
    path('my-channel/update/', channel_update, name='channel-update'),

    # user specific views
    path('my-profile/', my_profile, name='my-profile'),
    path('my-channel/', my_channel, name='my-channel'),

    # package views
    re_path(r'^tinymce/', include('tinymce.urls')),
    re_path(r'^accounts/', include('allauth.urls'))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

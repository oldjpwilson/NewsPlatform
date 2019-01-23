from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from core.views import my_profile_view, my_channel_view, channel_list, channel_create, channel_detail, channel_update

urlpatterns = [
    path('admin/', admin.site.urls),
    path('my-profile/', my_profile_view, name='profile'),
    path('my-channel/', channel_detail, name='channel'),
    path('profile/channel/update/', channel_update, name='update-channel'),
    path('explore/', channel_list, name='list-channel'),
    path('become-a-journalist/', channel_create, name='create-channel'),
    path('', include('articles.urls', namespace='articles')),
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

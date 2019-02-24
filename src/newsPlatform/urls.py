from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from articles.views import (
    about,
    contact,
    home,
    search,
    article_list,
    article_detail,
    article_create,
    article_update,
    article_delete
)

from core.views import (
    my_profile,
    my_channel,
    profile_update_account,
    profile_update_payment_details,
    channel_list,
    channel_create,
    channel_stats,
    channel_update,
    channel_update_payment_details,
    channel_public,
    subscribe,
    unsubscribe,
    remove_credit_card,
    StripeAuthorizeView,
    StripeAuthorizeCallbackView,
    create_payouts
)

from newsletter.views import profile_update_email_preferences

urlpatterns = [
    path('admin/', admin.site.urls),

    # home view
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),

    # article views
    path('news-feed/', article_list, name='article-list'),
    path('articles/<id>/', article_detail, name='article-detail'),
    path('create/', article_create, name='article-create'),
    path('articles/<id>/update/', article_update, name='article-update'),
    path('articles/<id>/delete/', article_delete, name='article-delete'),

    # profile views
    path('my-profile/', my_profile, name='my-profile'),
    path('my-profile/edit-account/',
         profile_update_account,
         name='edit-my-account'),
    path('my-profile/edit-payment-details',
         profile_update_payment_details,
         name='edit-profile-payment-details'),
    path('my-profile/edit-email-preferences/',
         profile_update_email_preferences,
         name='edit-email-preferences'),
    path('remove-credit-card/<card_id>/',
         remove_credit_card,
         name='remove-credit-card'),

    # channel views
    path('explore/', channel_list, name='channel-list'),
    path('become-a-journalist/', channel_create, name='channel-create'),
    path('my-channel/', my_channel, name='my-channel'),
    path('my-channel/stats/', channel_stats, name='channel-stats'),
    path('my-channel/edit-channel/', channel_update, name='edit-my-channel'),
    path('channel/<name>/', channel_public, name='channel-public'),
    path('my-channel/edit-payment-details/',
         channel_update_payment_details, name='edit-channel-payment-details'),

    # action views
    path('subscribe/<name>/', subscribe, name='subscribe'),
    path('unsubscribe/<name>/', unsubscribe, name='unsubscribe'),
    path('search/', search, name='search'),

    # stripe authorization views
    path('stripe-authorize/',
         StripeAuthorizeView.as_view(),
         name='stripe-authorization'),
    path('oauth/callback/',
         StripeAuthorizeCallbackView.as_view(),
         name='stripe-authorization-callback'),

    # stripe payout view
    path('create-payouts/<key>/', create_payouts, name='create-payouts'),

    # package views
    re_path(r'^tinymce/', include('tinymce.urls')),
    re_path(r'^accounts/', include('allauth.urls')),
    re_path(r'^ratings/', include('star_ratings.urls', namespace='ratings')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
#     urlpatterns += static(settings.STATIC_URL,
#                           document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)

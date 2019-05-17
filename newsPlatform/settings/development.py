from .base import *

DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', '1f656cab.ngrok.io']
WSGI_APPLICATION = 'newsPlatform.wsgi.application'

INSTALLED_APPS += [
    'debug_toolbar'
]

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]

# Debug toolbar

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': show_toolbar
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, "static_root")
MEDIA_ROOT = os.path.join(BASE_DIR, "media_root")

# Stripe

STRIPE_PUBLIC_KEY = 'pk_test_yvNsCGcWsZwGtj66YNA8lpip'
STRIPE_SECRET_KEY = 'sk_test_UST3EtJfUKd1GcvR1YrBH3RM'
STRIPE_CONNECT_CLIENT_ID = 'ca_EZbadnfmquQd3PcD8LdkIhIHbgSy0yqO'

DOMAIN = 'http://127.0.0.1:8000'
PAYMENTS_KEY = config('PAYMENTS_KEY')
BILL_KEY = config('BILL_KEY')

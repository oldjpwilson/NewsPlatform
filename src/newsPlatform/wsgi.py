import os
from django.conf import settings
from django.core.wsgi import get_wsgi_application

settings_module = 'newsPlatform.settings.production'
if settings.DEBUG:
    settings_module = 'newsPlatform.settings.development'


os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()

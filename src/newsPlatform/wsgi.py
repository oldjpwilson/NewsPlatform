import os
from decouple import config
from django.core.wsgi import get_wsgi_application

DEBUG = config('DEBUG')
settings_module = 'newsPlatform.settings.production'
if DEBUG is True:
    settings_module = 'newsPlatform.settings.development'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()

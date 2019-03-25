import os
from decouple import config
from django.core.wsgi import get_wsgi_application

settings_module = 'newsPlatform.settings.test'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()

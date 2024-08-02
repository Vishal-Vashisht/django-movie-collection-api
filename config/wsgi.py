"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import dotenv
from django.core.wsgi import get_wsgi_application

dotenv.load_dotenv()
env = os.getenv("ENVIRONMENT")
if env:
    if env not in ['development', 'production']:
        env = 'base'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings.{env or 'base'}')

application = get_wsgi_application()

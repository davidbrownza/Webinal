"""
WSGI config for Webinal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""
import os
import sys

root_path = '/srv/Webinal/'
sys.path.insert(0, '/srv/Webinal/venv/lib/python2.7/site-packages/')
sys.path.insert(0, '/srv/Webinal/')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Webinal.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

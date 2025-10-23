"""
WSGI config for project4 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

# For serving video stream.
from dj_static import Cling, MediaCling
from django.core.wsgi import get_wsgi_application
from static_ranges import Ranges

# TODO check for more modern pacakge to do the same.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project4.settings")

application = Ranges(Cling(MediaCling(get_wsgi_application())))

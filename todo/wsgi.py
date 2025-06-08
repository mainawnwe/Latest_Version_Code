"""
WSGI config for todo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

# Replace with your actual path
project_path = '/home/ackermancode/Latest_Version_code'
if project_path not in sys.path:
    sys.path.append(project_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'toto.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


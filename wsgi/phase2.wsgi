import os
import site
import sys

os.environ['CELERY_LOADER'] = 'django'
# Add the app dir to the python path so we can import manage.
wsgidir = os.path.dirname(__file__)

site.addsitedir(os.path.abspath(os.path.join(wsgidir, '..')))
site.addsitedir(os.path.abspath(os.path.join(wsgidir, '..', '..')))
site.addsitedir('/var/webapps/ignite-phase2/venv/lib/python2.6/site-packages/')

# manage adds /apps, /lib, and /vendor to the Python path.
import manage

os.environ['DJANGO_SETTINGS_MODULE'] = 'ignite-phase2.settings_local'
os.environ['DJANGO_SITE'] = 'ignite'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

# vim: ft=python

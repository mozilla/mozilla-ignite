import os
import site
import sys

os.environ['CELERY_LOADER'] = 'django'
# Add the app dir to the python path so we can import manage.
wsgidir = os.path.dirname(__file__)

path = lambda *x: os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '..', *x)

site.addsitedir(path('.'))
site.addsitedir(path('..'))

# manage adds /apps, /lib, and /vendor to the Python path.

# replicated from manage.py

# Adjust the python path and put local packages in front.
prev_sys_path = list(sys.path)
site.addsitedir(path('apps'))
site.addsitedir(path('lib'))

# Local (project) vendor library
site.addsitedir(path('vendor-local'))
site.addsitedir(path('vendor-local/lib/python'))

# Global (upstream) vendor library
site.addsitedir(path('vendor'))
site.addsitedir(path('vendor/lib/python'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'ignite_phase2.settings_local'
os.environ['DJANGO_SITE'] = 'ignite'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

# vim: ft=python

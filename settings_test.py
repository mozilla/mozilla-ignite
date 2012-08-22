import os

from settings_ignite import *

DEBUG = TEMPLATE_DEBUG = True

DEVELOPMENT_PHASE = True

BOOKING_THROTTLING_TIMEDELTA = 60 * 60 * 24  # 24 Hours

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


HMAC_KEYS = {
    '2011-01-01': 'cheesecake',
}


EXCLUDED_APPS = ('django_mailer', 'south', 'admin_tools',
                 'debug_toolbar')
INSTALLED_APPS = filter(lambda a: a not in EXCLUDED_APPS, INSTALLED_APPS)


NOSE_ARGS = [
    '-s',
    '--failed',
    '--stop',
    '--nocapture',
    '--failure-detail',
    '--with-progressive',
    '--logging-filter=-south',
    ]

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'


HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

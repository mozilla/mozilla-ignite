import os

if os.environ.get('DJANGO_SITE') == 'ignite':
    from settings_ignite import *
else:
    from settings import *

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


app_list = []

for app in INSTALLED_APPS:
    conditions = [not app == 'south',
                  not 'admin_tools' in app,
                  not 'debug_toolbar' in app,
                  not 'sentry' in app,
                  ]
    if all(conditions):
        app_list.append(app)

INSTALLED_APPS = app_list

# TEST_RUNNER = 'test_utils.runner.RadicalTestSuiteRunner'

NOSE_ARGS = [
    '-s',
    '--failed',
    '--stop',
    '--nocapture',
    '--failure-detail',
    '--with-progressive',
    # '--with-coverage',
    ]

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'


HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

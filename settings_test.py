from settings_local import *

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

# TEST_RUNNER = 'test_utils.runner.RadicalTestSuiteRunner'

NOSE_ARGS = [
    # '--with-spec',
    # '--spec-color',
    '-s',
    # '--with-coverage',
    ]
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

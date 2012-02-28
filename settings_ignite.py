from settings import *

# ROOT_PACKAGE comes from base settings
ROOT_URLCONF = '%s.urls_ignite' % ROOT_PACKAGE

IGNITE_PROJECT_SLUG = 'us-ignite'
IGNITE_CHALLENGE_SLUG = 'ignite-challenge'

FIXTURE_DIRS = (path('fixtures'),)

TEMPLATE_DIRS = (path('templates_ignite'),) + TEMPLATE_DIRS

EXCLUDED_MIDDLEWARE = ('commons.middleware.LocaleURLMiddleware',)

MIDDLEWARE_CLASSES = filter(lambda m: m not in EXCLUDED_MIDDLEWARE,
                            MIDDLEWARE_CLASSES)

TEMPLATE_CONTEXT_PROCESSORS += ('ignite.context_processors.browserid_target_processor',
                                'challenges.context_processors.assigned_submissions_processor',
                                'challenges.context_processors.current_phase',)

# Adds extra bits when the DEVELOPMENT_PHASE is enabled
if DEVELOPMENT_PHASE:
    TEMPLATE_DIRS = (
        path('templates_ignite', 'development'),
        ) + TEMPLATE_DIRS

from settings import *

# ROOT_PACKAGE comes from base settings
ROOT_URLCONF = '%s.urls_ignite' % ROOT_PACKAGE

IGNITE_SITE = True
IGNITE_PROJECT_SLUG = 'us-ignite'
IGNITE_CHALLENGE_SLUG = 'ignite-challenge'
IGNITE_IDEATION_NAME = 'Ideation'
IGNITE_DEVELOPMENT_NAME = 'Development'

EMAIL_SUBJECT_PREFIX = '[Mozilla Ignite] '

FIXTURE_DIRS = (path('fixtures'),)

TEMPLATE_DIRS = (path('templates_ignite'),) + TEMPLATE_DIRS

EXCLUDED_MIDDLEWARE = ('commons.middleware.LocaleURLMiddleware',)

MIDDLEWARE_CLASSES = filter(lambda m: m not in EXCLUDED_MIDDLEWARE,
                            MIDDLEWARE_CLASSES)

MIDDLEWARE_CLASSES += (
    'challenges.middleware.PhaseStatusMiddleware',
    'challenges.middleware.JudgeMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'ignite.context_processors.browserid_target_processor',
    'challenges.context_processors.assigned_submissions_processor',
    )


ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: "/profile/%s/" % u.username,
}

# ``DEVELOPMENT_PHASE`` only enables templating overriding
# any other functionality has been implemented using
# Phases/Rounds start and end dates.
if DEVELOPMENT_PHASE:
    TEMPLATE_DIRS = (
        path('templates_ignite', 'development'),
        ) + TEMPLATE_DIRS

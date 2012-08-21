from challenges.tests.fixtures.project_fixtures import *

# Add this dictionary to a form for no external links
BLANK_EXTERNALS = {
    'externals-TOTAL_FORMS': '1',
    'externals-INITIAL_FORMS': '0',
    'externals-MAX_NUM_FORMS': ''
    }

EXTERNALS = {
    'externals-TOTAL_FORMS': '2',
    'externals-INITIAL_FORMS': '0',
    'externals-MAX_NUM_FORMS': '',
    'externals-0-name': 'Mozilla',
    'externals-0-url': 'http://mozilla.org',
    'externals-1-name': '',
    'externals-1-url': '',
    }

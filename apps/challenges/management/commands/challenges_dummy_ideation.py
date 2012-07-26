import random

from StringIO import StringIO
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.template.defaultfilters import slugify
from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.conf import settings

from challenges.models import Submission, Category, Phase, Challenge, Project
import identicon

# Expected constants in the DB
IGNITE_PROJECT_SLUG = 'us-ignite'
IGNITE_CHALLENGE_SLUG = 'ignite-challenge'
IGNITE_IDEATION_NAME = 'Ideation'
IGNITE_DEVELOPMENT_NAME = 'Development'


def update_phase_date(phase, start_date, end_date, order):
    phase.start_date = start_date
    phase.end_date = end_date
    phase.order = order
    phase.save()
    return phase

# wording
d = open('/usr/share/dict/words', "r").readlines()
_random_words = lambda n: " ".join([random.choice(d).lower().rstrip() for i in range(n)])
_random_paragraph = lambda: _random_words(30).capitalize()
_random_paragraphs = lambda n: ".\n\n".join([_random_paragraph() for i in range(n)])


def _random_image(name):
    name = "dummy/dummy_%s.png" % name
    icon = identicon.render_identicon(random.randint(5 ** 5, 10 ** 10),
                                      random.randint(64, 250))
    # using storage
    tmp_file = StringIO()
    icon.save(tmp_file, 'PNG')
    return default_storage.save(name, ContentFile(tmp_file.getvalue()))

def create_user(handle):
    """Helper to create Users with a profile"""
    email = '%s@%s.com' % (handle, handle)
    user = User.objects.create_user(handle, email, handle)
    profile = user.get_profile()
    # middleware needs a name if not will redirect to edit
    profile.name = handle.title()
    profile.save()
    return profile

class Command(BaseCommand):
    help = """Bootstraps Mozilla Ignite data in the ideation phase, without the
    development phase changes. Used to simulate the current content on the site.
    This is only suitable to be run on a Development environment.
    """

    USERS = 50
    POST_PER_USER = 3


    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            raise CommandError("IMPORTANT: Make sure you only run this on a "
                               "Development environment ")
        print("Make sure, the project code base has NOT the development phase "
              "changes, before running this")
        answer = raw_input("Does the project codebase ONLY contain the "
                           "Ideation codebase (yes/no)? ")
        if answer != 'yes':
            raise CommandError("Make sure your codebase .")
        answer = raw_input("This will IRREVERSIBLY add TEST DATA to your "
                           "database. Proceed (yes/no)? ")
        if answer != 'yes':
            raise CommandError("Phew. Import canceled.")
        now = datetime.utcnow()
        project = Project.objects.get(slug=IGNITE_PROJECT_SLUG)
        challenge = Challenge.objects.get(slug=IGNITE_CHALLENGE_SLUG)
        ideation = Phase.objects.get(name=IGNITE_IDEATION_NAME)
        category = Category.objects.all()[0]
        try:
            development = Phase.objects.get(name=IGNITE_DEVELOPMENT_NAME)
        except Phase.DoesNotExist:
            development = None
        # Open ideation phase
        ideation = update_phase_date(ideation,
                                     now - relativedelta(days=3),
                                     now + relativedelta(days=30), 1)
        if development:
            development = update_phase_date(development,
                                            now + relativedelta(days=50),
                                            now + relativedelta(days=80), 2)
        for i in range(self.USERS):
            profile = create_user(slugify(_random_words(1)))
            for p in range(self.POST_PER_USER):
                data = {
                    'title': _random_words(4).title(),
                    'brief_description': _random_words(15),
                    'description': _random_paragraphs(5),
                    'category': category,
                    'life_improvements': _random_paragraphs(2),
                    'interest_making': _random_paragraphs(2),
                    'phase': ideation,
                    'created_by': profile,
                    'sketh_note': _random_image(slugify(_random_words(1))),
                    }
                submission = Submission.objects.create(**data)
        print "DONE!"

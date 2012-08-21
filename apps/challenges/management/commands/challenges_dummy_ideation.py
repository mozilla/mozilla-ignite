from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.template.defaultfilters import slugify
from django.core.management.base import BaseCommand, CommandError

from challenges.models import Submission, Category, Phase, Challenge, Project
from challenges.management.commands.dummy_utils import create_submissions

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


class Command(BaseCommand):
    help = """Bootstraps Mozilla Ignite data in the Ideation phase, without the
    development phase changes. Used to simulate the current content on the site.
    This is only suitable to be run on a Development environment.
    """


    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            raise CommandError("IMPORTANT: Make sure you only run this on a "
                               "Development environment ")
        print("Make sure, the project code base has NOT the development phase "
              "changes merged, before running this command")
        answer = raw_input("Does the project codebase ONLY contain the "
                           "Ideation codebase. (yes/no)? ")
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
        submission_list = create_submissions(ideation, category)
        print "DONE!", len(submission_list), "submissions created"

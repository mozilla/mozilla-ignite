import test_utils

from datetime import datetime

from badges.models import Badge, SubmissionBadge
from challenges.models import (Submission, Phase, Challenge, Category,
                               Project)
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from timeslot.tests.fixtures import create_project, create_challenge, create_phase


class BadgesBaseTest(test_utils.TestCase):
    """Setup for the Badges tests"""

    def setUp(self):
        """Actions to be performed at the beginning of each test"""
        # setup ignite challenge
        self.project = create_project(settings.IGNITE_PROJECT_SLUG)
        self.challenge = create_challenge(settings.IGNITE_CHALLENGE_SLUG,
                                          self.project)
        now = datetime.utcnow()
        past = now - relativedelta(days=30)
        future = now + relativedelta(days=30)
        # create the Ideation and Development phases
        idea_data = {'order': 1, 'start_date': past, 'end_date': now}
        self.ideation = create_phase(settings.IGNITE_IDEATION_NAME,
                                     self.challenge, idea_data)
        dev_data = {'order': 2, 'start_date': now, 'end_date': future}
        self.development = create_phase(settings.IGNITE_DEVELOPMENT_NAME,
                                        self.challenge, dev_data)

    def tearDown(self):
        """Actions to be performed at the end of each test"""
        for model in [Submission, Phase, Challenge, Category, Project,
                      User, Badge, SubmissionBadge]:
            model.objects.all().delete()

    def create_badge(self, **kwargs):
        defaults = {'badge_type': Badge.GREEN_LIT}
        defaults.update(kwargs)
        return Badge.objects.create(**defaults)

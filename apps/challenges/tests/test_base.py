import test_utils

from datetime import datetime

from challenges.models import (Submission, Phase, Challenge, Category,
                               Project)
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from timeslot.tests.fixtures import (create_project, create_challenge,
                                     create_phase)
from challenges.models import PhaseRound


class TestPhasesBase(test_utils.TestCase):

    def setUp(self):
        # setup ignite challenge
        self.project = create_project(settings.IGNITE_PROJECT_SLUG)
        self.challenge = create_challenge(settings.IGNITE_CHALLENGE_SLUG,
                                          self.project)
        self.now = datetime.utcnow()
        self.delta = relativedelta(days=30)
        self.past = self.now - self.delta
        self.future = self.now + self.delta
        # create the Ideation and Development phases
        idea_data = {'order': 1, 'start_date': self.now, 'end_date': self.now}
        self.ideation = create_phase(settings.IGNITE_IDEATION_NAME,
                                     self.challenge, idea_data)
        dev_data = {'order': 2, 'start_date': self.now, 'end_date': self.now}
        self.development = create_phase(settings.IGNITE_DEVELOPMENT_NAME,
                                        self.challenge, dev_data)
        self.request = RequestFactory().get('/')

    def tearDown(self):
        for model in [Submission, Phase, Challenge, Category, Project,
                      User, PhaseRound]:
            model.objects.all().delete()

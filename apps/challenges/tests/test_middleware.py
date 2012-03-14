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
from challenges.middleware import PhaseStatusMiddleware
from challenges.models import PhaseRound


class TestPhaseMiddlewareBase(test_utils.TestCase):

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


class TestIdeationPhaseMiddleware(TestPhaseMiddlewareBase):

    def setUp(self):
        """Setup the ideation phase as active"""
        super(TestIdeationPhaseMiddleware, self).setUp()
        self.ideation.start_date = self.now
        self.ideation.end_date = self.future
        self.ideation.save()
        self.development.start_date = self.future + relativedelta(days=1)
        self.development.end_date = self.future + self.delta
        self.development.save()

    def test_ideation_phase_open(self):
        PhaseStatusMiddleware().process_view(self.request)
        phase = self.request.phase
        expected = {
            'is_open': True,
            'name': settings.IGNITE_IDEATION_NAME,
            'days_remaining': 29,
            'phase_round': None,
            }
        for k, v in expected.items():
            self.assertEqual(phase[k], v)

    def test_ideation_phase_closed(self):
        # close the ideation phase for testing results
        self.ideation.start_date = self.past
        self.ideation.end_date = self.now - relativedelta(minutes=1)
        self.ideation.save()
        PhaseStatusMiddleware().process_view(self.request)
        phase = self.request.phase
        expected = {
            'is_open': False,
            'name': None,
            'days_remaining': -1,
            'phase_round': None,
            }
        for k, v in expected.items():
            self.assertEqual(phase[k], v)


class TestDevelopmentPhaseMiddleware(TestPhaseMiddlewareBase):

    def setUp(self):
        """Setup the development phase as active"""
        super(TestDevelopmentPhaseMiddleware, self).setUp()
        self.ideation.start_date = self.past
        self.ideation.end_date = self.past
        self.ideation.save()
        self.development.start_date = self.now
        self.development.end_date = self.future
        self.development.save()

    def test_development_phase_open(self):
        PhaseStatusMiddleware().process_view(self.request)
        phase = self.request.phase
        expected = {
            'is_open': True,
            'name': settings.IGNITE_DEVELOPMENT_NAME,
            'days_remaining': 29,
            'phase_round': None,
            }
        for k, v in expected.items():
            self.assertEqual(phase[k], v)

    def test_development_phase_closed(self):
        # set development phase in the past
        self.development.start_date = self.now - relativedelta(days=2)
        self.development.end_date = self.now - relativedelta(days=1)
        self.development.save()
        PhaseStatusMiddleware().process_view(self.request)
        phase = self.request.phase
        expected = {
            'is_open': False,
            'name': None,
            'days_remaining': -1,
            'phase_round': None,
            }
        for k, v in expected.items():
            self.assertEqual(phase[k], v)


class TestDevelopmentPhaseRoundsMiddleware(TestPhaseMiddlewareBase):

    def setUp(self):
        """Setup the development phase as active"""
        super(TestDevelopmentPhaseRoundsMiddleware, self).setUp()
        self.ideation.start_date = self.past
        self.ideation.end_date = self.past
        self.ideation.save()
        self.development.start_date = self.now - relativedelta(days=10)
        self.development.end_date = self.future
        self.development.save()

    def create_round(self, **kwargs):
        """Creates a Round"""
        defaults = {
            'name': 'Phase Round',
            'phase': self.development,
            'start_date': self.development.start_date,
            'end_date': self.development.end_date,
            }
        if kwargs:
            defaults.update(kwargs)
        instance, created = PhaseRound.objects.get_or_create(**defaults)
        return instance

    def test_development_round_open(self):
        item = self.create_round()
        PhaseStatusMiddleware().process_view(self.request)
        phase = self.request.phase
        expected = {
            'is_open': True,
            'name': settings.IGNITE_DEVELOPMENT_NAME,
            'days_remaining': 29,
            'phase_round': item.name,
            }
        for k, v in expected.items():
            self.assertEqual(phase[k], v)

    def test_development_round_closed(self):
        # set the end date of the round in the past
        end_date = self.now - relativedelta(days=1)
        item = self.create_round(end_date=end_date)
        PhaseStatusMiddleware().process_view(self.request)
        phase = self.request.phase
        expected = {
            'is_open': False,
            'name': settings.IGNITE_DEVELOPMENT_NAME,
            'days_remaining': -1,
            'phase_round': None,
            }
        for k, v in expected.items():
            self.assertEqual(phase[k], v)

    def test_multiple_development_rounds(self):
        end_date = self.now - relativedelta(days=1)
        round_1 = self.create_round(end_date=end_date)
        round_2 = self.create_round(name='Round 2', start_date=self.now)
        PhaseStatusMiddleware().process_view(self.request)
        phase = self.request.phase
        expected = {
            'is_open': True,
            'name': settings.IGNITE_DEVELOPMENT_NAME,
            'days_remaining': 29,
            'phase_round': round_2.name,
            }
        for k, v in expected.items():
            self.assertEqual(phase[k], v)

    def test_multiple_development_rounds_closed(self):
        end_date = self.now - relativedelta(days=1)
        round_1 = self.create_round(end_date=end_date)
        start_date = self.now + relativedelta(days=1)
        round_2 = self.create_round(name='Round 2', start_date=start_date)
        PhaseStatusMiddleware().process_view(self.request)
        phase = self.request.phase
        expected = {
            'is_open': False,
            'name': settings.IGNITE_DEVELOPMENT_NAME,
            'days_remaining': -1,
            'phase_round': None,
            }
        for k, v in expected.items():
            self.assertEqual(phase[k], v)

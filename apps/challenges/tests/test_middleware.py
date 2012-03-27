from datetime import datetime

from challenges.middleware import PhaseStatusMiddleware
from challenges.tests.fixtures.ignite_fixtures import (setup_ignite_challenge,
                                                       teardown_ignite_challenge,
                                                       setup_ideation_phase,
                                                       setup_development_phase)
from django.conf import settings
from django.test.client import RequestFactory
from test_utils import TestCase


class TestPhaseMiddleware(TestCase):

    def setUp(self):
        self.now = datetime.utcnow()
        self.request = RequestFactory().get('/')

    def tearDown(self):
        teardown_ignite_challenge()


class TestIdeationPhaseMiddleware(TestPhaseMiddleware):

    def setUp(self):
        """Setup the ideation phase as active"""
        self.initial_data = setup_ideation_phase(**setup_ignite_challenge())
        self.ideation = self.initial_data['ideation_phase']
        self.development = self.initial_data['dev_phase']
        super(TestIdeationPhaseMiddleware, self).setUp()

    def test_ideation_phase_open(self):
        PhaseStatusMiddleware().process_view(self.request)
        expected = {
            'is_open': True,
            'name': settings.IGNITE_IDEATION_NAME,
            'days_remaining': 9,
            'phase_round': None,
            }
        for k, v in expected.items():
            self.assertEqual(self.request.phase[k], v)
        return


class TestIdeationClosedMiddleware(TestPhaseMiddleware):

    def setUp(self):
        self.initial_data = setup_ideation_phase(is_open=False,
                                                 **setup_ignite_challenge())
        super(TestIdeationClosedMiddleware, self).setUp()

    def test_ideation_phase_closed(self):
        PhaseStatusMiddleware().process_view(self.request)
        expected = {
            'is_open': False,
            'name': None,
            'days_remaining': -1,
            'phase_round': None,
            }
        for k, v in expected.items():
            self.assertEqual(self.request.phase[k], v)
        return


class TestDevelopmentPhaseMiddleware(TestPhaseMiddleware):

    def setUp(self):
        self.initial_data = setup_development_phase(**setup_ignite_challenge())
        super(TestDevelopmentPhaseMiddleware, self).setUp()

    def test_development_phase_open(self):
        PhaseStatusMiddleware().process_view(self.request)
        phase = self.request.phase
        expected = {
            'is_open': True,
            'name': settings.IGNITE_DEVELOPMENT_NAME,
            'days_remaining': 9,
            'phase_round': 'Round A',
            }
        for k, v in expected.items():
            self.assertEqual(phase[k], v)


class DevelopmentPhaseClosedMiddleware(TestPhaseMiddleware):

    def setUp(self):
        self.initial_data = setup_development_phase(is_round_open=False,
                                                    **setup_ignite_challenge())
        super(DevelopmentPhaseClosedMiddleware, self).setUp()

    def test_development_phase_closed(self):
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
        return

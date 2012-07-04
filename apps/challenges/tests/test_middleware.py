from datetime import datetime

from challenges.middleware import PhaseStatusMiddleware
from challenges.tests.fixtures.ignite_fixtures import (setup_ignite_challenge,
                                                       teardown_ignite_challenge,
                                                       setup_ideation_phase,
                                                       setup_development_phase)
from django.conf import settings
from django.test.client import RequestFactory
from test_utils import TestCase
from nose.tools import ok_, eq_


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
        ideation = self.request.ideation
        ok_(ideation)
        ok_(ideation.is_open)
        eq_(ideation.name, settings.IGNITE_IDEATION_NAME)
        eq_(ideation.days_remaining, 9)
        eq_(ideation.current_round, None)
        development = self.request.development
        eq_(development, self.development)
        eq_(development.is_open, False)
        eq_(development.name, settings.IGNITE_DEVELOPMENT_NAME)
        eq_(development.days_remaining, -1)
        eq_(development.current_round, None)

class TestIdeationClosedMiddleware(TestPhaseMiddleware):

    def setUp(self):
        self.initial_data = setup_ideation_phase(is_open=False,
                                                 **setup_ignite_challenge())
        self.ideation = self.initial_data['ideation_phase']
        self.development = self.initial_data['dev_phase']
        super(TestIdeationClosedMiddleware, self).setUp()

    def test_ideation_phase_closed(self):
        PhaseStatusMiddleware().process_view(self.request)
        ideation = self.request.ideation
        ok_(ideation)
        eq_(ideation.is_open, False)
        eq_(ideation.name, settings.IGNITE_IDEATION_NAME)
        eq_(ideation.days_remaining, -1)
        eq_(ideation.current_round, None)
        development = self.request.development
        eq_(development, self.development)
        eq_(development.is_open, False)
        eq_(development.name, settings.IGNITE_DEVELOPMENT_NAME)
        eq_(development.days_remaining, -1)
        eq_(development.current_round, None)


class TestDevelopmentPhaseMiddleware(TestPhaseMiddleware):

    def setUp(self):
        self.initial_data = setup_development_phase(**setup_ignite_challenge())
        self.ideation = self.initial_data['ideation_phase']
        self.development = self.initial_data['dev_phase']
        super(TestDevelopmentPhaseMiddleware, self).setUp()

    def test_development_phase_open(self):
        PhaseStatusMiddleware().process_view(self.request)
        ideation = self.request.ideation
        eq_(ideation, self.ideation)
        eq_(ideation.is_open, False)
        eq_(ideation.name, settings.IGNITE_IDEATION_NAME)
        eq_(ideation.days_remaining, -1)
        eq_(ideation.current_round, None)
        development = self.request.development
        eq_(development, self.development)
        eq_(development.is_open, True)
        eq_(development.name, settings.IGNITE_DEVELOPMENT_NAME)
        eq_(development.days_remaining, 9)
        ok_(development.current_round)


class DevelopmentPhaseClosedMiddleware(TestPhaseMiddleware):

    def setUp(self):
        self.initial_data = setup_development_phase(is_round_open=False,
                                                    **setup_ignite_challenge())
        self.ideation = self.initial_data['ideation_phase']
        self.development = self.initial_data['dev_phase']
        super(DevelopmentPhaseClosedMiddleware, self).setUp()

    def test_development_phase_closed(self):
        PhaseStatusMiddleware().process_view(self.request)
        ideation = self.request.ideation
        eq_(ideation, self.ideation)
        eq_(ideation.is_open, False)
        eq_(ideation.name, settings.IGNITE_IDEATION_NAME)
        eq_(ideation.days_remaining, -1)
        eq_(ideation.current_round, None)
        development = self.request.development
        eq_(development, self.development)
        eq_(development.is_open, False)
        eq_(development.name, settings.IGNITE_DEVELOPMENT_NAME)
        eq_(development.days_remaining, -1)
        eq_(development.current_round, None)

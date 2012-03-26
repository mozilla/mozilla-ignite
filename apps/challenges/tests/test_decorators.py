from challenges.decorators import phase_open_required
from challenges.tests.fixtures.ignite_fixtures import (setup_ignite_challenge,
                                                       teardown_ignite_challenge,
                                                       setup_ideation_phase,
                                                       setup_development_phase,
                                                       create_submission,
                                                       create_user)
from django.http import HttpResponseForbidden, HttpResponse
from django.test.client import RequestFactory
from test_utils import TestCase


class TestPhasesOpenDecorator(TestCase):

    def setUp(self):
        """Setup the ideation phase as close"""
        self.initial_data = setup_ideation_phase(is_open=False,
                                                 **setup_ignite_challenge())
        self.ideation = self.initial_data['ideation_phase']
        self.development = self.initial_data['dev_phase']
        self.phase_data = {
            'is_open': False,
            'name': None,
            'days_remaining': -1,
            'phase_round': None,
            }

    def tearDown(self):
        teardown_ignite_challenge()

    def test_default_block(self):
        """Test all the views are blocked by default"""
        # mock of a simple view
        @phase_open_required
        def sample_view(request):
            return HttpResponse('OK')

        request = RequestFactory().get('/')
        # mock the closed phase data
        request.phase = self.phase_data
        response = sample_view(request)
        self.assertTrue(isinstance(response, HttpResponseForbidden))

    def test_post_block(self):
        # mock of a simple view
        @phase_open_required(methods_allowed=['GET'])
        def sample_view(request):
            return HttpResponse('OK')

        request = RequestFactory().get('/')
        # mock the closed phase data
        request.phase = self.phase_data
        response = sample_view(request)
        # GET is allowed
        self.assertTrue(response.status_code, 200)
        request = RequestFactory().post('/', {})
        # mock the closed phase data
        request.phase = self.phase_data
        response = sample_view(request)
        # POST is not allowed
        self.assertTrue(isinstance(response, HttpResponseForbidden))

    def test_get_block(self):
        # mock of a simple view
        @phase_open_required(methods_allowed=['POST'])
        def sample_view(request):
            return HttpResponse('OK')

        request = RequestFactory().get('/')
        # mock the closed phase data
        request.phase = self.phase_data
        response = sample_view(request)
        # GET is not allowed
        self.assertTrue(isinstance(response, HttpResponseForbidden))
        request = RequestFactory().post('/', {})
        # mock the closed phase data
        request.phase = self.phase_data
        response = sample_view(request)
        # POST is allowed
        self.assertTrue(response.status_code, 200)

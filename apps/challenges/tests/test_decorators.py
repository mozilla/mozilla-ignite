from challenges.decorators import phase_open_required
from challenges.tests.test_base import TestPhasesBase
from dateutil.relativedelta import relativedelta
from django.http import HttpResponseForbidden, HttpResponse
from django.test.client import RequestFactory


class TestPhasesOpenDecorator(TestPhasesBase):

    def setUp(self):
        """Setup the ideation phase as close"""
        super(TestPhasesOpenDecorator, self).setUp()
        self.ideation.start_date = self.past
        self.ideation.end_date = self.now - relativedelta(days=1)
        self.ideation.save()
        self.development.start_date = self.future
        self.development.end_date = self.future + self.delta
        self.development.save()
        self.phase_data = {
            'is_open': False,
            'name': None,
            'days_remaining': -1,
            'phase_round': None,
            }

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

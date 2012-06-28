from django.core.exceptions import ImproperlyConfigured

from challenges.decorators import phase_open_required, phase_required
from mock import MagicMock
from nose.tools import eq_, raises
from test_utils import TestCase, RequestFactory


phase_mock = MagicMock()
phase_mock.is_open = False
phase_open_mock = MagicMock()
phase_open_mock.is_open = True


@phase_open_required
def mock_phase_view(request, **kwargs):
    return kwargs

@phase_open_required(methods_allowed=['GET'])
def mock_phase_view_get(request, **kwargs):
    return kwargs


class TestOpenPhaseRequiredDecorator(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.ideation = phase_open_mock

    def test_decorator_defaults(self):
        response = mock_phase_view(self.request, phase='ideation')
        eq_(response['phase'], 'ideation')

    def test_phase_method_allowed(self):
        response = mock_phase_view_get(self.request, phase='ideation')
        eq_(response['phase'], 'ideation')

    def test_phase_method_not_allowed(self):
        request = self.factory.post('/', {})
        request.ideation = phase_open_mock
        response = mock_phase_view(request, phase='ideation')
        eq_(response['phase'], 'ideation')


class TestClosedPhaseRequiredDecorator(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.ideation = phase_mock

    def test_decorator_defaults(self):
        response = mock_phase_view(self.request, phase='ideation')
        eq_(response.status_code, 403)

    def test_phase_method_allowed(self):
        response = mock_phase_view_get(self.request, phase='ideation')
        eq_(response['phase'], 'ideation')

    def test_phase_method_not_allowed(self):
        request = self.factory.post('/', {})
        request.ideation = phase_mock
        response = mock_phase_view_get(request, phase='ideation')
        eq_(response.status_code, 403)


@phase_required(methods_allowed=['GET'], is_open=True)
def mock_view(request, **kwargs):
    return kwargs


@phase_required
def mock_default_view(request, **kwargs):
    return kwargs


class TestPhaseRequiredDecorator(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.ideation = phase_mock

    def test_method_allowed(self):
        response = mock_view(self.request, phase='ideation')
        eq_(response['phase'], 'ideation')

    def test_method_not_allowed(self):
        request = self.factory.post('/', {})
        request.ideation = phase_mock
        response = mock_view(request, phase='ideation')
        eq_(response.status_code, 403)

    @raises(ImproperlyConfigured)
    def test_invalid_phase(self):
        mock_view(self.request, phase='development')

    def test_defaults(self):
        response = mock_default_view(self.request, phase='ideation')
        eq_(response.status_code, 403)

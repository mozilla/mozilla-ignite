from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.test import Client
from django.test.client import RequestFactory

from mock import MagicMock
from projects.models import Project
from ignite.tests.decorators import ignite_skip
from innovate import urls
from innovate.views import handle404, handle500


@ignite_skip
def test_routes():
    c = Client()
    for pattern in urls.urlpatterns:
        response = c.get(reverse(pattern.name))
        assert response.status_code == 301
        assert response.has_header('location')
        location = response.get('location', None)
        assert location is not None
        response = c.get(location)
        assert response.status_code == 200


@ignite_skip
def test_featured():
    project = Project.objects.create(
        name=u'Test Project',
        slug=u'test-project',
        description=u'Blah',
        featured=True
    )
    c = Client()
    response = c.get('/en-US/')
    assert response.status_code == 200
    assert project.name in response.content

development = MagicMock
development.has_started = False

def test_404_handler():
    """Test that the 404 error handler renders and gives the correct code."""
    request = RequestFactory().get('/not/a/real/path/')
    request.user = AnonymousUser()
    request.development = development
    response = handle404(request)
    assert response.status_code == 404

def test_500_handler():
    """Test that the 500 error handler renders and gives the correct code."""
    request = RequestFactory().get('/not/a/real/path/')
    request.user = AnonymousUser()
    request.development = development
    response = handle500(request)
    assert response.status_code == 500

from datetime import datetime, timedelta

from django.http import Http404
from django.test.client import Client
from mock import Mock
from nose.tools import assert_equal, with_setup
import test_utils

from challenges import views
from challenges.models import Challenge, Submission
from projects.models import Project


def challenge_setup():
    """Set up some sample data to test with.
    
    This is a bit clearer and hopefully more flexible than using fixtures.
    
    """
    challenge_teardown()  # In case other tests didn't clean up
    
    p = Project()
    p.name, p.slug = 'My Project', 'my-project'
    p.description = 'My super awesome project of awesomeness.'
    p.long_description = 'Did I mention how awesome it was?'
    p.allow_participation = True
    p.save()
    
    c = Challenge()
    c.project = p
    c.title, c.slug = 'My Challenge', 'my-challenge'
    c.summary = 'Are you up to it?'
    c.description = 'This is a challenge of supreme challengingness.'
    c.end_date = datetime.now() + timedelta(days=365)
    c.save()


def challenge_teardown():
    """Tear down any data created by these tests."""
    for model in [Project, Challenge, Submission]:
        model.objects.all().delete()


def _build_request(path=None):
    request = Mock()
    request.path = path
    request._messages = []  # Stop messaging code trying to iterate a Mock
    return request


@with_setup(challenge_setup, challenge_teardown)
def test_show_challenge():
    """Test the view to show an individual challenge."""
    request = _build_request('/my-project/my-challenge/')
    response = views.show(request, 'my-project', 'my-challenge')
    assert_equal(response.status_code, 200)


class ChallengeEntryTest(test_utils.TestCase):
    # Need to inherit from this base class to get Jinja2 template hijacking
    
    def setUp(self):
        challenge_setup()
    
    def tearDown(self):
        challenge_teardown()
    
    def test_no_entries(self):
        """Test that challenges display ok without any entries."""
        response = self.client.get('/en-US/my-project/challenges/my-challenge/')
        assert_equal(response.status_code, 200)
        # Make sure the entries are present and in reverse creation order
        assert_equal(len(response.context['entries']), 0)
    
    def test_challenge_entries(self):
        """Test that challenge entries come through to the challenge view."""
    
        for i in range(1, 4):
            Submission.objects.create(title='Submission %d' % i,
                                      brief_description='A submission',
                                      description='A really good submission',
                                      challenge=Challenge.objects.get())
    
        response = self.client.get('/en-US/my-project/challenges/my-challenge/')
        assert_equal(response.status_code, 200)
        # Make sure the entries are present and in reverse creation order
        assert_equal([s.title for s in response.context['entries']],
                     ['Submission %d' % i for i in [3, 2, 1]])


@with_setup(challenge_setup, challenge_teardown)
def test_challenge_not_found():
    """Test behaviour when a challenge doesn't exist."""
    request = _build_request('/my-project/not-a-challenge/')
    try:
        response = views.show(request, 'my-project', 'not-a-challenge')
    except Http404:
        pass
    else:
        assert_equal(response.status_code, 404)


@with_setup(challenge_setup, challenge_teardown)
def test_wrong_project():
    """Test behaviour when the project and challenge don't match."""
    project_fields = {'name': 'Another project', 'slug': 'another-project',
                      'description': "Not the project you're looking for",
                      'long_description': 'Nothing to see here'}
    other_project = Project.objects.create(**project_fields)
    request = _build_request('/another-project/my-challenge/')
    # We either want 404 by exception or by response code here: either is fine
    try:
        response = views.show(request, 'another-project', 'my-challenge')
    except Http404:
        pass
    else:
        assert_equal(response.status_code, 404)

from datetime import datetime, timedelta

from mock import Mock
from nose.tools import assert_equal, with_setup

from challenges import views
from challenges.models import Challenge
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
    for model in [Project, Challenge]:
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

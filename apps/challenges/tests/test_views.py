from datetime import datetime, timedelta

from django.contrib.auth.models import User
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
    for model in [Submission, Challenge, Project, User]:
        model.objects.all().delete()


def _build_request(path=None):
    request = Mock()
    request.path = path
    request._messages = []  # Stop messaging code trying to iterate a Mock
    return request


def _create_submissions(count, challenge=None):
    """Create a number of fake submissions. Return their titles.
    
    If a challenge is not supplied, assume only one challenge exists.
    
    """
    if challenge is None:
        challenge = Challenge.objects.get()
    titles = ['Submission %d' % i for i in range(1, count + 1)]
    for title in titles:
        Submission.objects.create(title=title,
                                  brief_description='A submission',
                                  description='A really good submission',
                                  challenge=challenge)
    return titles


def _create_users():
    for name in ['alex', 'bob', 'charlie']:
        User.objects.create_user(name, '%s@example.com' % name, password=name)


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
        submission_titles = _create_submissions(3)
        response = self.client.get('/en-US/my-project/challenges/my-challenge/')
        assert_equal(response.status_code, 200)
        # Make sure the entries are present and in reverse creation order
        assert_equal([s.title for s in response.context['entries']],
                     list(reversed(submission_titles)))
    
    def test_entries_view(self):
        """Test the dedicated entries view.
        
        This is currently a thin proxy onto the challenge view, hence this test
        being practically identical to the one above.
        
        """
        submission_titles = _create_submissions(4)
        response = self.client.get('/en-US/my-project/challenges/my-challenge/entries/')
        assert_equal(response.status_code, 200)
        # Make sure the entries are present and in reverse creation order
        assert_equal([s.title for s in response.context['entries']],
                     list(reversed(submission_titles)))


class CreateEntryTest(test_utils.TestCase):
    """Tests related to posting a new entry."""
    
    def setUp(self):
        challenge_setup()
        self.project_slug, self.challenge_slug = (Project.objects.get().slug,
                                                  Challenge.objects.get().slug)
        self.entry_form_path = '/en-US/%s/challenges/%s/entries/add/' % \
                               (self.project_slug, self.challenge_slug)
        _create_users()
    
    def tearDown(self):
        challenge_teardown()
    
    def test_display_form(self):
        """Test the new entry form."""
        self.client.login(username='alex', password='alex')
        response = self.client.get(self.entry_form_path)
        assert_equal(response.status_code, 200)
        # Check nothing gets created
        assert_equal(Submission.objects.count(), 0)
    
    def test_submit_form(self):
        self.client.login(username='alex', password='alex')
        form_data = {'title': 'Submission',
                     'brief_description': 'A submission',
                     'description': 'A submission of shining wonderment.',
                     'created_by': User.objects.get(username='alex').id}
        response = self.client.post(self.entry_form_path, data=form_data,
                                    follow=True)
        redirect_target = '/en-US/%s/challenges/%s/' % (self.project_slug,
                                                        self.challenge_slug)
        self.assertRedirects(response, redirect_target)
        # Make sure we actually created the submission
        assert_equal([s.description for s in Submission.objects.all()],
                     ['A submission of shining wonderment.'])
        submission = Submission.objects.get()
        assert_equal(submission.challenge.slug, self.challenge_slug)
        creator_names = submission.created_by.values_list('user__username')
        assert_equal(list(creator_names), [('alex',)])
    
    def test_invalid_form(self):
        """Test that an empty form submission fails with errors."""
        self.client.login(username='alex', password='alex')
        response = self.client.post(self.entry_form_path, data={})
        # Not so fussed about authors: we'll be re-working that soon enough
        assert all(k in response.context['errors']
                   for k in ['title', 'description'])
        assert_equal(Submission.objects.count(), 0)


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

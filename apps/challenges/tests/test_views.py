from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test.client import Client
from mock import Mock, patch
from nose.tools import assert_equal, with_setup
import test_utils

from commons.middleware import LocaleURLMiddleware
from challenges import views
from challenges.models import Challenge, Submission, Phase
from projects.models import Project


# Apply this decorator to a test to turn off the middleware that goes around
# inserting 'en_US' redirects into all the URLs
suppress_locale_middleware = patch.object(LocaleURLMiddleware,
                                          'process_request',
                                          lambda *args: None)


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
    
    ph = Phase()
    ph.challenge = c
    ph.name = 'Phase 1'
    ph.order = 1
    ph.save()


def challenge_teardown():
    """Tear down any data created by these tests."""
    for model in [Submission, Phase, Challenge, Project, User]:
        model.objects.all().delete()


def _build_request(path=None):
    request = Mock()
    request.path = path
    request._messages = []  # Stop messaging code trying to iterate a Mock
    return request


def _create_submissions(count, phase=None, creator=None):
    """Create a number of fake submissions. Return their titles.
    
    If a phase is not supplied, assume only one phase exists.
    
    If a creator is not supplied, try to get a single user's profile, or create
    a dummy user.
    
    """
    if phase is None:
        phase = Phase.objects.get()
    
    if creator is None:
        try:
            user = User.objects.get()
        except User.DoesNotExist:
            user = User.objects.create_user('bob', 'bob@example.com', 'bob')
        creator = user.get_profile()
    
    titles = ['Submission %d' % i for i in range(1, count + 1)]
    for title in titles:
        Submission.objects.create(title=title,
                                  brief_description='A submission',
                                  description='A really good submission',
                                  phase=phase,
                                  created_by=creator)
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
    
    def test_anonymous_form(self):
        """Check we can't display the entry form without logging in."""
        response = self.client.get(self.entry_form_path)
        # Check it's some form of redirect
        assert response.status_code in xrange(300, 400)
    
    def test_anonymous_post(self):
        """Check we can't post an entry without logging in."""
        form_data = {'title': 'Submission',
                     'brief_description': 'A submission',
                     'description': 'A submission of shining wonderment.',
                     'created_by': User.objects.get(username='alex').id}
        response = self.client.post(self.entry_form_path, data=form_data)
        assert response.status_code in xrange(300, 400)
        assert_equal(Submission.objects.count(), 0)
    
    def test_display_form(self):
        """Test the new entry form."""
        self.client.login(username='alex', password='alex')
        response = self.client.get(self.entry_form_path)
        assert_equal(response.status_code, 200)
        # Check nothing gets created
        assert_equal(Submission.objects.count(), 0)
    
    def test_submit_form(self):
        self.client.login(username='alex', password='alex')
        alex = User.objects.get(username='alex')
        form_data = {'title': 'Submission',
                     'brief_description': 'A submission',
                     'description': 'A submission of shining wonderment.',
                     'created_by': alex.get_profile()}
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
        assert_equal(submission.created_by.user, alex)
    
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


class ShowEntryTest(test_utils.TestCase):
    """Test functionality of the single entry view."""
    
    def setUp(self):
        challenge_setup()
        _create_users()
        alex_profile = User.objects.get(username='alex').get_profile()
        s = Submission.objects.create(phase=Phase.objects.get(),
                                      title='A submission',
                                      brief_description='My submission',
                                      description='My wonderful submission',
                                      created_by=alex_profile)
        s.save()
        
        self.submission_path = '/en-US/%s/challenges/%s/entries/%d/' % \
                               (Project.objects.get().slug,
                                Challenge.objects.get().slug,
                                Submission.objects.get().id)
    
    def test_show_entry(self):
        response = self.client.get(self.submission_path)
        assert_equal(response.status_code, 200)
    
    def test_entry_not_found(self):
        # Just double-check a submission with that ID doesn't exist
        assert 19 not in Submission.objects.values_list('id', flat=True)
        bad_path = '/en-US/my-project/challenges/my-challenge/entries/19/'
        response = self.client.get(bad_path)
        assert_equal(response.status_code, 404, response.content)


class EditEntryTest(test_utils.TestCase):
    """Test functionality of the edit entry view."""
    
    def setUp(self):
        challenge_setup()
        _create_users()
        
        admin = User.objects.create_user('admin', 'admin@example.com',
                                         password='admin')
        admin.is_superuser = True
        admin.save()
        
        alex_profile = User.objects.get(username='alex').get_profile()
        _create_submissions(1, creator=alex_profile)
        
        entry_id = Submission.objects.get().id
        
        base_kwargs = {'project': Project.objects.get().slug,
                       'slug': Challenge.objects.get().slug}
        
        view_kwargs = dict(entry_id=entry_id, **base_kwargs)
        self.view_path = reverse('entry_show', kwargs=view_kwargs)
        
        edit_kwargs = dict(pk=entry_id, **base_kwargs)
        self.edit_path = reverse('entry_edit', kwargs=edit_kwargs)
    
    @suppress_locale_middleware
    def test_edit_form(self):
        self.client.login(username='alex', password='alex')
        
        response = self.client.get(self.edit_path)
        assert_equal(response.status_code, 200)
    
    @suppress_locale_middleware
    def test_edit(self):
        self.client.login(username='alex', password='alex')
        data = dict(title=Submission.objects.get().title,
                    brief_description='A submission',
                    description='A really, seriously good submission')
        response = self.client.post(self.edit_path, data)
        self.assertRedirects(response, self.view_path)
        assert_equal(Submission.objects.get().description, data['description'])
    
    @suppress_locale_middleware
    def test_anonymous_access(self):
        """Check that anonymous users can't get at the form."""
        response = self.client.get(self.edit_path)
        assert_equal(response.status_code, 302)
    
    @suppress_locale_middleware
    def test_anonymous_edit(self):
        """Check that anonymous users can't post to the form."""
        data = dict(title=Submission.objects.get().title,
                    brief_description='A submission',
                    description='A really, seriously good submission')
        response = self.client.post(self.edit_path, data)
        assert_equal(response.status_code, 302)
        assert 'seriously' not in Submission.objects.get().description
    
    @suppress_locale_middleware
    def test_non_owner_access(self):
        """Check that non-owners cannot see the edit form."""
        self.client.login(username='bob', password='bob')
        response = self.client.get(self.edit_path)
        assert_equal(response.status_code, 403)
    
    @suppress_locale_middleware
    def test_non_owner_edit(self):
        """Check that users cannot edit each other's submissions."""
        self.client.login(username='bob', password='bob')
        data = dict(title=Submission.objects.get().title,
                    brief_description='A submission',
                    description='A really, seriously good submission')
        response = self.client.post(self.edit_path, data)
        assert_equal(response.status_code, 403)
        assert 'seriously' not in Submission.objects.get().description
    
    @suppress_locale_middleware
    def test_admin_access(self):
        """Check that administrators can see the edit form."""
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.edit_path)
        assert_equal(response.status_code, 200)
    
    @suppress_locale_middleware
    def test_admin_edit(self):
        """Check that administrators can edit submissions."""
        self.client.login(username='admin', password='admin')
        data = dict(title=Submission.objects.get().title,
                    brief_description='A submission',
                    description='A really, seriously good submission')
        response = self.client.post(self.edit_path, data)
        self.assertRedirects(response, self.view_path)
        assert_equal(Submission.objects.get().description, data['description'])

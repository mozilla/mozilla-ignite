from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from mock import Mock, patch

from projects.models import Project
from challenges.models import Challenge, Submission, Phase


def _create_project_and_challenge():
    """Create and return a sample project with a sample challenge."""
    project = Project.objects.create(name='Project', slug='project',
                                          allow_participation=True)
    end_date = datetime.now() + timedelta(days=365)
    challenge = Challenge.objects.create(title='Challenge',
                                              slug='challenge',
                                              end_date=end_date,
                                              project=project)
    return project, challenge


class PermalinkTest(TestCase):
    
    def setUp(self):
        self.project, self.challenge = _create_project_and_challenge()
    
    def test_permalink(self):
        self.assertEqual(self.challenge.get_absolute_url(),
                         '/project/challenges/challenge/')
    
    def tearDown(self):
        for model in [Challenge, Project]:
            model.objects.all().delete()


class SingleChallengePermalinkTest(TestCase):
    
    urls = 'challenges.tests.single_challenge_urls'
    
    def setUp(self):
        self.project, self.challenge = _create_project_and_challenge()
    
    def test_single_challenge_permalink(self):
        """Test permalink generation on an Ignite-style one-challenge site."""
        self.assertEqual(self.challenge.get_absolute_url(), '/')
    
    def tearDown(self):
        for model in [Challenge, Project]:
            model.objects.all().delete()


class EntriesToLive(TestCase):
    
    def setUp(self):
        self.project = Project.objects.create(
            name=u'A project for a test',
            allow_participation=True
        )
        self.challenge = Challenge.objects.create(
            title=u'Testing my submissions',
            end_date=u'2020-11-30 12:23:28',
            project=self.project,
            moderate=True
        )
        self.phase = Phase.objects.create(
            name=u'Phase 1', challenge=self.challenge, order=1
        )
        self.user = User.objects.create_user('bob', 'bob@example.com', 'bob')
        self.submission = Submission.objects.create(
            title=u'A submission to test',
            description=u'<h3>Testing bleach</h3>',
            is_live=True,
            phase=self.phase,
            created_by=self.user.get_profile()
        )

    def test_entry_hidden(self):
        """
        The user wants the entry to go live but it needs moderating first
        """
        self.assertEqual(self.submission.is_live, False)
    
    def test_phase_unicode(self):
        """Test the string representation of a phase."""
        self.assertEqual(unicode(self.phase),
                         u'Phase 1 (Testing my submissions)')
    
    def test_bleach_clearning(self):
        """
        Check that we're stripping out bad content - <h3> isn't in our 
        allowed list
        """
        self.assertEqual(self.submission.description_html,
                         '&lt;h3&gt;Testing bleach&lt;/h3&gt;')

from django.test import TestCase

from projects.models import Project
from challenges.models import Challenge, Submission


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
        self.submission = Submission.objects.create(
            title=u'A submission to test',
            description=u'<h3>Testing bleach</h3>',
            is_live=True,
            challenge=self.challenge
        )

    def test_entry_hidden(self):
        """
        The user wants the entry to go live but it needs moderating first
        """
        self.assertEqual(self.submission.is_live, False)

    def test_bleach_clearning(self):
        """
        Check that we're stripping out bad content - <h3> isn't in our 
        allowed list
        """
        self.assertEqual(self.submission.description_html,
                         '&lt;h3&gt;Testing bleach&lt;/h3&gt;')

from django.test import TestCase

from projects.models import Project
from participation.models import Participation, Entry


class EntriesToLive(TestCase):
    
    def setUp(self):
        self.Project = Project.objects.create(
            name=u'A project for a test',
            allow_participation=True
        )
        self.Participation = Participation.objects.create(
            title=u'Testing my entries',
            end_date=u'2020-11-30 12:23:28',
            project=self.Project,
            moderate=True
        )
        self.Entry = Entry.objects.create(
            title=u'An entry to test',
            description=u'<h3>Testing bleach</h3>',
            is_live=True,
            participation=self.Participation
        )

    def test_entry_hidden(self):
        """
        The user wants the entry to go live but it needs moderating first
        """
        self.assertEqual(self.Entry.is_live, False)

    def test_bleach_clearning(self):
        """
        Check that we're stripping out bad content - <h3> isn't in our 
        allowed list
        """
        self.assertEqual(self.Entry.description_html, '&lt;h3&gt;Testing bleach&lt;/h3&gt;')

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
            is_live=True,
            participation=self.Participation
        )

    def test_entry_hidden(self):
        """
        The user wants the entry to go live but it needs moderating first
        """
        self.assertEqual(self.Entry.is_live, False)

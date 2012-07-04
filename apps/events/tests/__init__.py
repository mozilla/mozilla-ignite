import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from events.models import Event
from challenges.tests.fixtures import create_users

class EventTest(TestCase):

    def setUp(self):
        name = 'bob'
        self.user = User.objects.create_user(name, '%s@example.com' % name,
                                             password=name)

    def TearDown(self):
        Event.objects.all().delete()
        User.objects.all().delete()

    def test_event_creation(self):
        data = {
            'name': 'Ignite event',
            'slug': 'ignite-event',
            'start': datetime.datetime.now(),
            'end': datetime.datetime.now(),
            'description': '',
            'url': 'mozilla.org',
            'author': self.user,
            }

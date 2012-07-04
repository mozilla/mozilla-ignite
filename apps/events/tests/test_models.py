import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from events.models import Event, Venue


class EventTest(TestCase):

    def setUp(self):
        name = 'bob'
        user = User.objects.create_user(name, '%s@example.com' % name,
                                        password=name)
        self.profile = user.get_profile()
        self.profile.name = name
        self.profile.save()

    def TearDown(self):
        Event.objects.all().delete()
        User.objects.all().delete()

    def create_event(self, **kwargs):
        defaults = {
            'name': 'Ignite event',
            'slug': 'ignite-event',
            'start': datetime.datetime.now(),
            'end': datetime.datetime.now(),
            'description': '',
            'url': 'mozilla.org',
            'created_by': self.profile,
            }
        if kwargs:
            defaults.update(kwargs)
        return Event.objects.create(**defaults)

    def test_event_creation(self):
        data = {
            'name': 'Ignite event',
            'slug': 'ignite-event',
            'start': datetime.datetime.now(),
            'end': datetime.datetime.now(),
            'description': '',
            'url': 'mozilla.org',
            'created_by': self.profile,
            }
        event = Event.objects.create(**data)
        assert event.id, "Couldn't create event"
        self.assertFalse(event.featured)

    def test_featured_events(self):
        self.create_event(slug='event-a', featured=True)
        self.create_event(slug='event-b', featured=False)
        self.assertEqual(Event.objects.all().count(), 2)
        self.assertEqual(Event.objects.get_featured().count(), 1)


class VenueTest(TestCase):

    def tearDown(self):
        Venue.objects.all().delete()

    def test_venue_creation(self):
        data = {
            'name': 'Mozilla HQ',
            'slug': 'mozilla-hq',
            }
        venue = Venue.objects.create(**data)
        assert venue.id, "Couldn't create venue"

from datetime import datetime, timedelta

from challenges.tests.fixtures.ignite_fixtures import setup_ignite_challenge
from dateutil.relativedelta import relativedelta
from test_utils import TestCase
from timeslot.models import TimeSlot, Release
from timeslot.tests.fixtures import create_release, create_timeslot


class TimeSlotModelTest(TestCase):

    def setUp(self):
        self.initial_data = setup_ignite_challenge()
        self.ideation = self.initial_data['ideation_phase']
        self.development = self.initial_data['dev_phase']

    def test_release_creation(self):
        """Create a Release with the minimum data"""
        data = {'name': 'Release',
                'is_current': True,
                'phase': self.ideation}
        release = Release.objects.create(**data)
        assert release.id, "Failed to create release"

    def test_current_release_creation(self):
        """Test the current release mechanics"""
        release = create_release('Release', True, self.ideation)
        self.assertEqual(release, Release.objects.get_current())
        self.assertEqual(Release.objects.filter(is_current=True).count(), 1)
        # add an extra current release
        new_release = create_release('New release', True, self.development)
        self.assertEqual(new_release, Release.objects.get_current())
        self.assertEqual(Release.objects.filter(is_current=True).count(), 1)

    def test_create_timeslot(self):
        """Create a ``TimeSlot`` with the less possible data"""
        release = create_release('Release', True, self.ideation)
        data = {
            'start_date': datetime.utcnow(),
            'end_date': datetime.utcnow() + relativedelta(hours=1),
            'release': release,
            }
        timeslot = TimeSlot.objects.create(**data)
        assert timeslot.id, "TimeSlot not created"

    def test_timeslot_releases(self):
        """Test the available ``TimeSlots`` for a given ``Release``"""
        release_a = create_release('Release A', True, self.ideation)
        for i in range(2):
            create_timeslot(release_a)
        self.assertEqual(TimeSlot.available.all().count(), 2)
        release_b = create_release('Release B', True, self.ideation)
        self.assertEqual(TimeSlot.available.all().count(), 0)
        for i in range(2):
            create_timeslot(release_b)
        self.assertEqual(TimeSlot.available.all().count(), 2)
        self.assertEqual(TimeSlot.objects.all().count(), 4)

    def test_upcoming_timeslots(self):
        release_a = create_release('Release A', True, self.ideation)
        for i in range(2):
            create_timeslot(release_a)
        self.assertEqual(TimeSlot.objects.all().count(), 2)
        self.assertEqual(TimeSlot.objects.upcoming().count(), 0)
        TimeSlot.objects.all().update(is_booked=True)
        self.assertEqual(TimeSlot.objects.upcoming().count(), 2)

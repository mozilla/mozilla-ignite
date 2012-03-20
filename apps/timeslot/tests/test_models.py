import test_utils

from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from timeslot.models import TimeSlot, Release
from timeslot.tests.fixtures import create_release
from timeslot.tests.test_base import TimeSlotBaseTest


class TimeSlotModelTest(TimeSlotBaseTest):

    def create_timeslot(self, release, extra_data=None):
        """Helper to add ``TimeSlots`` with the minium required data"""
        # booking of timeslots start at least 24 hours in advance
        start_date = datetime.utcnow() + timedelta(hours=25)
        end_date = start_date + timedelta(minutes=60)
        data = {
            'start_date': start_date,
            'end_date': end_date,
            'release': release,
            }
        if extra_data:
            data.update(extra_data)
        return TimeSlot.objects.create(**data)

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

    def create_simple_timeslot(self):
        """Create a ``TimeSlot`` with the less possible data"""
        release = Release.objects.create(name='Release', is_current=True)
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
        for i in range(5):
            self.create_timeslot(release_a)
        self.assertEqual(TimeSlot.available.all().count(), 5)
        release_b = create_release('Release B', True, self.ideation)
        self.assertEqual(TimeSlot.available.all().count(), 0)
        for i in range(5):
            self.create_timeslot(release_b)
        self.assertEqual(TimeSlot.available.all().count(), 5)
        self.assertEqual(TimeSlot.objects.all().count(), 10)

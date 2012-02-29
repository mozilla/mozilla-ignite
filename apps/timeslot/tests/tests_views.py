import test_utils

from datetime import datetime, timedelta

from challenges.tests import fixtures
from challenges.models import Submission
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from timeslot.models import TimeSlot


class TimeSlotTest(test_utils.TestCase):
    """Tests for the ``TimeSlot`` mechanics
    IMPORTANT: to use the ``client`` you require to extend the ``test_utils``
    """

    def setUp(self):
        """actions to be performed at the beginning of each test"""
        fixtures.challenge_setup()

    def tearDown(self):
        """Actions to be performed at the end of each test"""
        fixtures.challenge_teardown()
        User.objects.all().delete()
        TimeSlot.objects.all().delete()

    def add_timeslot(self, extra_data=None):
        """Helper to add ``TimeSlots`` with the minium required data"""
        data = {
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(minutes=60)
            }
        if extra_data:
            data.update(extra_data)
        return TimeSlot.objects.create(**data)

    def create_user(self, handle, extra_data=None):
        """Helper to create Users with a profile"""
        email = '%s@%s.com' % (handle, handle)
        user = User.objects.create_user(handle, email, handle)
        profile = user.get_profile()
        # middleware needs a name if not will redirect to edit
        profile.name = handle
        profile.save()
        return profile

    def help_timeslot_creation(self):
        """Test the ``TimeSlot`` creation"""
        for i in range(20):
            self.add_timeslot()
        self.assertEqual(TimeSlot.objects.all().count(), 20)

    def test_timeslot_protected(self):
        """Test the listing of the TimeSlots"""
        self.help_timeslot_creation()
        # use the first submission
        user = self.create_user('bob')
        fixtures.create_submissions(20, creator=user)
        entry = Submission.objects.all()[0]
        booking_url = reverse('timeslot:object_list', args=[entry.id])
        # Booking timetables are protected
        response = self.client.get(booking_url)
        login_url = reverse('login')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(login_url in response['Location'])

    def test_timeslot_no_win(self):
        """Test the ``TimeSlot`` when entries are not winners"""
        self.help_timeslot_creation()
        user = self.create_user('bob')
        fixtures.create_submissions(20, creator=user)
        # Booking time tables are only available for winner entries
        self.client.login(username='bob', password='bob')
        # All submissions shouldn't be accessible
        for tmp_entry in Submission.objects.all():
            tmp_url = reverse('timeslot:object_list', args=[tmp_entry.id])
            response = self.client.get(tmp_url)
            # If entry can't access should return a returns a 404
            self.assertEqual(response.status_code, 404)

    def test_timeslot_winner(self):
        """Test a winning entry"""
        # Mark entry as winner and make sure it renders
        self.help_timeslot_creation()
        # use the first submission
        user = self.create_user('bob')
        fixtures.create_submissions(20, creator=user)
        entry = Submission.objects.all()[0]
        booking_url = reverse('timeslot:object_list', args=[entry.id])
        entry.is_winner = True
        entry.save()
        self.client.login(username='bob', password='bob')
        response = self.client.get(booking_url)
        self.assertEqual(response.status_code, 200)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 20)


    def test_timeslot_booking(self):
        """Test the booking of a timeslot"""
        # book the first entry
        self.help_timeslot_creation()
        # use the first submission
        user = self.create_user('bob')
        fixtures.create_submissions(20, creator=user)
        entry = Submission.objects.all()[0]
        entry.is_winner = True
        entry.save()
        self.client.login(username='bob', password='bob')
        timeslot = TimeSlot.objects.all()[0]
        timeslot_url = reverse('timeslot:object_detail',
                               args=[entry.id, timeslot.short_id])
        response = self.client.post(timeslot_url, {})
        self.assertRedirects(response, entry.get_absolute_url())


    def test_duplicate_booking(self):
        """Test the behaviour on a booked ``Submission``"""
        self.help_timeslot_creation()
        # use the first submission
        user = self.create_user('bob')
        fixtures.create_submissions(20, creator=user)
        entry = Submission.objects.all()[0]
        entry.is_winner = True
        entry.save()
        self.client.login(username='bob', password='bob')
        # perform the booking
        timeslot = TimeSlot.objects.all()[0]
        timeslot_url = reverse('timeslot:object_detail',
                               args=[entry.id, timeslot.short_id])
        response = self.client.post(timeslot_url, {})
        # try to list should return to the submission homepage and
        # indicate this has been booked
        booking_url = reverse('timeslot:object_list', args=[entry.id])
        response = self.client.get(booking_url)
        self.assertRedirects(response, entry.get_absolute_url())
        # Redirect as well if user is trying to book another for the same
        # project
        timeslot = TimeSlot.objects.all()[2]
        timeslot_url = reverse('timeslot:object_detail',
                               args=[entry.id, timeslot.short_id])
        response = self.client.post(timeslot_url, {})
        self.assertRedirects(response, entry.get_absolute_url())

import test_utils

from datetime import datetime, timedelta

from challenges.models import Submission, Phase, Challenge, Project
from django.core.urlresolvers import reverse
from timeslot.models import TimeSlot
from timeslot.tests.fixtures import create_user, create_release, create_submission
from timeslot.tests.test_base import TimeSlotBaseTest


class TimeSlotTest(TimeSlotBaseTest):
    """Tests for the ``TimeSlot`` mechanics"""

    SUBMISSIONS = 5

    def setUp(self):
        """Actions to be performed at the beginning of each test"""
        super(TimeSlotTest, self).setUp()
        # create a winning submission
        self.name = 'bob'
        self.profile = create_user(self.name)
        self.submission = create_submission('Winner submission',
                                            self.profile, self.ideation,
                                            extra_data={'is_winner': True})
        self.listing_url = reverse('timeslot:object_list',
                                args=[self.submission.id])
        # create a list of submissions
        self.submission_list = self.generate_submissions(self.SUBMISSIONS)

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

    def get_booking_url(self, entry_id, short_id):
        return reverse('timeslot:object_detail', args=[entry_id, short_id])

    def generate_timeslots(self, total, release=None):
        """Create a number of ``TimeSlots`` with an active ``Release``"""
        release = release if release else create_release('Release', True)
        return [self.create_timeslot(release) for i in range(total)]

    def generate_submissions(self, total, user=None, are_winners=True):
        """Generates a nubmer of submissions"""
        for i in range(total):
            yield create_submission('Submission %s' % i,
                                    user if user else create_user('u%s' % i),
                                    self.ideation, {'is_winner': are_winners})

    def test_timeslot_protected(self):
        """Test the listing of the TimeSlots is secured"""
        self.generate_timeslots(self.SUBMISSIONS)
        # Booking timetables are protected
        response = self.client.get(self.listing_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(reverse('login') in response['Location'])

    def test_timeslot_listing_non_greenlit(self):
        """Test the ``TimeSlot`` when ``Submissions`` aren't green lit"""
        self.generate_timeslots(self.SUBMISSIONS)
        non_lit = [create_submission('Submission %s' % i, self.profile,
                                     self.ideation) for i in range(10)]
        # Booking time tables are only available for winner entries
        self.client.login(username=self.name, password=self.name)
        # All submissions shouldn't be accessible
        for entry in non_lit:
            url = reverse('timeslot:object_list', args=[entry.id])
            response = self.client.get(url)
            # If entry isn't green_lit returns a 404
            self.assertEqual(response.status_code, 404)

    def test_timeslot_listing_not_owned(self):
        """Test ``TimeSlot`` listing on not owned green-lit ``Submissions``"""
        self.generate_timeslots(self.SUBMISSIONS)
        self.client.login(username=self.name, password=self.name)
        for entry in self.submission_list:
            url = reverse('timeslot:object_list', args=[entry.id])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)

    def test_timeslot_listing_greenlit(self):
        """Test ``TimeSlot`` listing on a green lit ``Submission``"""
        self.generate_timeslots(self.SUBMISSIONS)
        self.client.login(username=self.name, password=self.name)
        # Timeslots should be available for my winning submission
        response = self.client.get(self.listing_url)
        self.assertEqual(response.status_code, 200)
        page = response.context['page']
        self.assertEqual(page.paginator.count, self.SUBMISSIONS)

    def test_timeslot_booking_non_greenlit(self):
        """Test ``TimeSlots`` bookings on non-green-lit ``Submissions``"""
        t1, t2 = self.generate_timeslots(2)
        non_lit = [create_submission('Submission %s' % i, self.profile,
                                     self.ideation) for i in range(10)]
        # Booking time tables are only available for winner entries
        self.client.login(username=self.name, password=self.name)
        # All submissions shouldn't be accessible
        for entry in non_lit:
            url = self.get_booking_url(entry.id, t1.short_id)
            response = self.client.get(url)
            response = self.client.post(url, {})
            self.assertEqual(response.status_code, 404)

    def test_timeslot_booking_not_owned(self):
        """Test``TimeSlot`` booking on not owned ``Submissions``"""
        t1, t2 = self.generate_timeslots(2)
        self.client.login(username=self.name, password=self.name)
        for entry in self.submission_list:
            url = self.get_booking_url(entry.id, t1.short_id)
            response = self.client.get(url)
            response = self.client.post(url, {})
            self.assertEqual(response.status_code, 404)

    def test_timeslot_booking_greenlit(self):
        """Test ``TimeSlot`` booking on a green lit ``Submission``"""
        t1, t2 = self.generate_timeslots(2)
        self.client.login(username=self.name, password=self.name)
        url = self.get_booking_url(self.submission.id, t1.short_id)
        response = self.client.get(url)
        # booking only available via POST
        self.assertEqual(response.status_code, 405)
        response = self.client.post(url, {}, follow=True)
        self.assertRedirects(response, self.submission.get_absolute_url())
        self.assertTrue('messages' in response.context)
        for item in list(response.context['messages']):
            self.assertTrue('successful' in item.message)

    def test_timeslot_double_booking(self):
        """Test an attempts to double book a green-lit ``Submission``"""
        t1, t2 = self.generate_timeslots(2)
        self.client.login(username=self.name, password=self.name)
        url = self.get_booking_url(self.submission.id, t1.short_id)
        # Perform the booking, follow the response triggers any
        # confirmation message
        response = self.client.post(url, {}, follow=True)
        # Attempt booking with a different and a duplicate timeslot
        for t in [t1, t2]:
            double_url = self.get_booking_url(self.submission.id, t.short_id)
            response = self.client.post(double_url, {}, follow=True)
            self.assertRedirects(response, self.submission.get_absolute_url())
            self.assertTrue('messages' in response.context)
            for item in list(response.context['messages']):
                self.assertTrue('already booked' in item.message)

    def test_post_booking_timeslot(self):
        """Test the behaviour after a successful ``TimeSlot`` booking"""
        t1, t2 = self.generate_timeslots(2)
        self.client.login(username=self.name, password=self.name)
        url = self.get_booking_url(self.submission.id, t1.short_id)
        # Perform the booking, follow the response triggers any
        # confirmation message
        self.client.post(url, {}, follow=True)
        # TimeSlots are reduced by one
        self.assertEqual(TimeSlot.available.all().count(), 1)
        # And listing is disallowed
        response = self.client.get(self.listing_url, follow=True)
        self.assertRedirects(response, self.submission.get_absolute_url())
        self.assertTrue('messages' in response.context)
        for item in list(response.context['messages']):
            self.assertTrue('already booked' in item.message)

    def test_timeslot_releases(self):
        """Test ``TimeSlots`` available for different releases"""
        release_a = create_release('Release A', True)
        self.generate_timeslots(self.SUBMISSIONS, release_a)
        self.client.login(username=self.name, password=self.name)
        response = self.client.get(self.listing_url)
        # timeslots available for this ``Release``
        self.assertEqual(response.context['page'].paginator.count,
                         self.SUBMISSIONS)
        release_b = create_release('Release B', True)
        response = self.client.get(self.listing_url)
        # New current release hides other TimeSlots
        self.assertEqual(response.context['page'].paginator.count, 0)
        self.generate_timeslots(self.SUBMISSIONS, release_b)
        response = self.client.get(self.listing_url)
        # New TimeSlot for this Release
        self.assertEqual(response.context['page'].paginator.count,
                         self.SUBMISSIONS)

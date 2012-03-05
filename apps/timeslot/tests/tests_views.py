import test_utils

from datetime import datetime, timedelta

from challenges.models import (Submission, Phase, Challenge, Category,
                               Project)
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from timeslot.models import TimeSlot
from timeslot.tests.fixtures import (create_project, create_challenge,
                                     create_phase, create_user,
                                     create_category, create_submission)


class TimeSlotTest(test_utils.TestCase):
    """Tests for the ``TimeSlot`` mechanics"""

    SUBMISSIONS = 20

    def setUp(self):
        """Actions to be performed at the beginning of each test"""
        # setup ignite challenge
        self.project = create_project(settings.IGNITE_PROJECT_SLUG)
        self.challenge = create_challenge(settings.IGNITE_CHALLENGE_SLUG,
                                          self.project)
        now = datetime.utcnow()
        past = now - timedelta(days=30)
        future = now + timedelta(days=30)
        # create the Ideation and Development phases
        idea_data = {'order': 1, 'start_date': past, 'end_date': now}
        self.ideation = create_phase(settings.IGNITE_IDEATION_NAME,
                                     self.challenge, idea_data)
        dev_data = {'order': 2, 'start_date': now, 'end_date': future}
        self.development = create_phase(settings.IGNITE_DEVELOPMENT_NAME,
                                        self.challenge, dev_data)

    def tearDown(self):
        """Actions to be performed at the end of each test"""
        Submission.objects.all().delete()
        Phase.objects.all().delete()
        Challenge.objects.all().delete()
        Category.objects.all().delete()
        Project.objects.all().delete()
        TimeSlot.objects.all().delete()
        User.objects.all().delete()

    def create_timeslot(self, extra_data=None):
        """Helper to add ``TimeSlots`` with the minium required data"""
        # booking of timeslots start at least 24 hours in advance
        start_date = datetime.utcnow() + timedelta(hours=25)
        end_date = start_date + timedelta(minutes=60)
        data = {
            'start_date': start_date,
            'end_date': end_date,
            }
        if extra_data:
            data.update(extra_data)
        return TimeSlot.objects.create(**data)

    def generate_timeslots(self, total):
        """Create a number of ``TimeSlots``"""
        return [self.create_timeslot() for i in range(total)]

    def test_timeslot_protected(self):
        """Test the listing of the TimeSlots is secured"""
        # use the first submission
        profile = create_user('bob')
        submission = create_submission('Winner submission',
                                       profile, self.ideation,
                                       extra_data={'is_winner': True})
        # make timeslots available
        self.generate_timeslots(5)
        booking_url = reverse('timeslot:object_list', args=[submission.id])
        # Booking timetables are protected
        response = self.client.get(booking_url)
        login_url = reverse('login')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(login_url in response['Location'])

    def test_timeslot_failed_submission(self):
        """Test the ``TimeSlot`` when entries are not winners"""
        self.generate_timeslots(self.SUBMISSIONS)
        profile = create_user('bob')
        # create failed submissions
        entry_list = [create_submission('Fail submission %s' % i, profile,
                                        self.ideation) \
                                        for i in range(self.SUBMISSIONS)]
        # Booking time tables are only available for winner entries
        self.client.login(username='bob', password='bob')
        # All submissions shouldn't be accessible
        for tmp_entry in entry_list:
            tmp_url = reverse('timeslot:object_list', args=[tmp_entry.id])
            response = self.client.get(tmp_url)
            # If entry isn't green_lit returns a 404
            self.assertEqual(response.status_code, 404)

    def test_timeslot_winner(self):
        """Test a winning entry"""
        timeslots = self.generate_timeslots(self.SUBMISSIONS)
        profile = create_user('bob')
        # create winner submissions
        data = {'is_winner': True}
        entry_list = [create_submission('Submission %s' % i, profile,
                                        self.ideation, extra_data=data) \
                                        for i in range(self.SUBMISSIONS)]
        self.client.login(username='bob', password='bob')
        # Timeslots should be availables
        for tmp_entry in entry_list:
            booking_url = reverse('timeslot:object_list', args=[tmp_entry.id])
            response = self.client.get(booking_url)
            self.assertEqual(response.status_code, 200)
            page = response.context['page']
            self.assertEqual(page.paginator.count, self.SUBMISSIONS)

    def test_timeslot_booking(self):
        """Test the booking of a timeslot"""
        timeslot_list = self.generate_timeslots(self.SUBMISSIONS)
        profile = create_user('bob')
        # create winner submissions
        data = {'is_winner': True}
        entry_list = [create_submission('Submission %s' % i, profile,
                                        self.ideation, extra_data=data) \
                                        for i in range(self.SUBMISSIONS)]
        self.client.login(username='bob', password='bob')
        # Book available timeslots
        for i, (entry, timeslot) in enumerate(zip(entry_list, timeslot_list),
                                              start=1):
            timeslot_url = reverse('timeslot:object_detail',
                                   args=[entry.id, timeslot.short_id])
            response = self.client.post(timeslot_url, {}, follow=True)
            self.assertRedirects(response, entry.get_absolute_url())
            self.assertTrue('messages' in response.context)
            for item in list(response.context['messages']):
                self.assertTrue('successful' in item.message)
            # Available timeslots reduce as bookings go on
            self.assertEqual(TimeSlot.objects.filter(is_booked=False).count(),
                             self.SUBMISSIONS - i)

    def test_booked_timeslot(self):
        """Test the behaviour on a booked ``Submission``"""
        timeslot_list = self.generate_timeslots(self.SUBMISSIONS)
        profile = create_user('bob')
        # create winner submissions
        data = {'is_winner': True}
        entry_list = [create_submission('Submission %s' % i, profile,
                                        self.ideation, extra_data=data) \
                                        for i in range(self.SUBMISSIONS)]
        self.client.login(username='bob', password='bob')
        # Book available timeslots
        for i, (entry, timeslot) in enumerate(zip(entry_list, timeslot_list),
                                              start=1):
            timeslot_url = reverse('timeslot:object_detail',
                                   args=[entry.id, timeslot.short_id])
            response = self.client.post(timeslot_url, {})
            self.assertRedirects(response, entry.get_absolute_url())
            # check available timeslots
            self.assertEqual(TimeSlot.objects.filter(is_booked=False).count(),
                             self.SUBMISSIONS - i)
            # trying to list any booking should redirect to the project
            booking_url = reverse('timeslot:object_list', args=[entry.id])
            response = self.client.get(booking_url, follow=True)
            self.assertTrue('messages' in response.context)
            for item in list(response.context['messages']):
                self.assertTrue('already booked' in item.message)
            self.assertRedirects(response, entry.get_absolute_url())
            # try to re-book the next available booking
            if self.SUBMISSIONS > i:
                timeslot_url = reverse('timeslot:object_detail',
                                       args=[entry.id, timeslot_list[i].short_id])
                response = self.client.post(timeslot_url, {}, follow=True)
                # redirect to the project homepage if user tries to rebook
                self.assertRedirects(response, entry.get_absolute_url())
                for item in list(response.context['messages']):
                    self.assertTrue('already booked' in item.message)
                # timeslots available should be the same
                self.assertEqual(TimeSlot.objects.filter(is_booked=False).count(),
                                 self.SUBMISSIONS - i)


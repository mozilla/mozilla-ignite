from datetime import datetime, timedelta

from challenges.models import Submission, SubmissionParent
from challenges.tests.fixtures.ignite_fixtures import (setup_ignite_challenge,
                                                       teardown_ignite_challenge,
                                                       setup_ideation_phase,
                                                       setup_development_phase,
                                                       create_submission,
                                                       create_user)
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from test_utils import TestCase
from timeslot.models import TimeSlot, Release
from timeslot.tests.fixtures import create_release, create_timeslot


class TimeSlotBaseTest(TestCase):

    def setUp(self):
        self.profile = create_user('bob')
        self.url = reverse('create_entry')

    def tearDown(self):
        teardown_ignite_challenge()
        for model in [Release, TimeSlot, SubmissionParent, Submission, User]:
            model.objects.all().delete()

    def assertRedirectsLogin(self, response):
        login_url = reverse('login')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(login_url in response['Location'])

    def generate_submissions(self, total, phase, user=None, are_winners=True):
        """Generates a nubmer of submissions"""
        for i in range(total):
            user = user if user else create_user('u%s' % i),
            yield create_submission(title='Submission %s' % i,
                                    created_by=user, phase=phase,
                                    is_winner=are_winners)

    def generate_timeslots(self, total, phase, release=None):
        """Create a number of ``TimeSlots`` with an active ``Release``"""
        release = release if release else create_release('Release', True, phase)
        return [create_timeslot(release) for i in range(total)]

    def get_booking_url(self, entry_id, short_id):
        return reverse('timeslot:object_detail', args=[entry_id, short_id])


class TimeSlotIdeationTest(TimeSlotBaseTest):

    def setUp(self):
        self.initial_data = setup_ideation_phase(**setup_ignite_challenge())
        self.ideation = self.initial_data['ideation_phase']
        self.development = self.initial_data['dev_phase']
        super(TimeSlotIdeationTest, self).setUp()
        self.submission = create_submission(created_by=self.profile,
                                            phase=self.ideation,
                                            is_winner=True)
        self.listing_url = reverse('timeslot:object_list',
                                   args=[self.submission.id])
        self.t1, self.t2 = self.generate_timeslots(2, self.ideation)
        self.booking_url = reverse('timeslot:object_detail',
                                   args=[self.submission.id,
                                         self.t1.short_id])

    def test_timeslot_listing_anon(self):
        """Test the listing of the TimeSlots is secured"""
        # Booking timetables are protected
        response = self.client.get(self.listing_url)
        self.assertRedirectsLogin(response)

    def test_timeslot_listing_non_greenlit(self):
        """Test the ``TimeSlot`` when ``Submissions`` aren't green lit"""
        non_lit = create_submission(title='Submission B',
                                    created_by=self.profile,
                                    phase=self.ideation)
        # Booking time tables are only available for winner entries
        self.client.login(username='bob', password='bob')
        response = self.client.get(reverse('timeslot:object_list',
                                           args=[non_lit.id]))
        self.assertEqual(response.status_code, 404)

    def test_timeslot_listing_not_owned(self):
        """Test ``TimeSlot`` listing on not owned green-lit ``Submissions``"""
        create_user('alex')
        self.client.login(username='alex', password='alex')
        response = self.client.get(self.listing_url)
        self.assertEqual(response.status_code, 404)

    def test_timeslot_listing_greenlit(self):
        """Test ``TimeSlot`` listing on a green lit ``Submission``"""
        self.client.login(username='bob', password='bob')
        # Timeslots should be available for my winning submission
        response = self.client.get(self.listing_url)
        self.assertEqual(response.status_code, 200)
        page = response.context['page']
        self.assertEqual(page.paginator.count, 2)

    def test_timeslot_booking_anon(self):
        response = self.client.get(self.booking_url)
        self.assertRedirectsLogin(response)

    def test_timeslot_booking_non_greenlit(self):
        """Test ``TimeSlots`` bookings on non-green-lit ``Submissions``"""
        non_lit = create_submission(title='Submission B',
                                    created_by=self.profile,
                                    phase=self.ideation)
        # Booking time tables are only available for winner entries
        self.client.login(username='bob', password='bob')
        url = self.get_booking_url(non_lit.id, self.t1.short_id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 404)

    def test_timeslot_booking_not_owned(self):
        """Test``TimeSlot`` booking on not owned ``Submissions``"""
        create_user('alex')
        self.client.login(username='alex', password='alex')
        response = self.client.get(self.booking_url)
        self.assertEqual(response.status_code, 405)
        response = self.client.post(self.booking_url, {})
        self.assertEqual(response.status_code, 404)

    def test_timeslot_booking_greenlit(self):
        """Test ``TimeSlot`` booking on a green lit ``Submission``"""
        self.client.login(username='bob', password='bob')
        # booking only available via POST
        response = self.client.get(self.booking_url)
        self.assertEqual(response.status_code, 405)
        # Perform booking
        response = self.client.post(self.booking_url, {}, follow=True)
        self.assertRedirects(response, self.submission.get_absolute_url())
        self.assertTrue('messages' in response.context)
        for item in list(response.context['messages']):
            self.assertEqual(item.tags, 'success')

    def test_timeslot_double_booking(self):
        """Test an attempts to double book a green-lit ``Submission``"""
        self.client.login(username='bob', password='bob')
        # Follow the response triggers any confirmation message
        response = self.client.post(self.booking_url, {}, follow=True)
        # Attempt booking with a different and a duplicate timeslot
        url = self.get_booking_url(self.submission.id, self.t2.short_id)
        response = self.client.post(url, {}, follow=True)
        self.assertRedirects(response, self.submission.get_absolute_url())
        self.assertTrue('messages' in response.context)
        for item in list(response.context['messages']):
            self.assertEqual(item.tags, 'error')

    def test_post_booking_timeslot(self):
        """Test the behaviour after a successful ``TimeSlot`` booking"""
        self.client.login(username='bob', password='bob')
        # Follow the response triggers any confirmation message
        self.client.post(self.booking_url, {}, follow=True)
        # TimeSlots are reduced by one
        self.assertEqual(TimeSlot.available.all().count(), 1)
        # And listing is disallowed
        response = self.client.get(self.listing_url, follow=True)
        self.assertRedirects(response, self.submission.get_absolute_url())
        for item in list(response.context['messages']):
            self.assertEqual(item.tags, 'error')

    def test_new_release_same_phase(self):
        release = create_release('Release B', True, self.ideation)
        self.client.login(username='bob', password='bob')
        response = self.client.get(self.listing_url)
        self.assertEqual(response.context['page'].paginator.count, 0)
        self.generate_timeslots(2, self.ideation, release=release)
        response = self.client.get(self.listing_url)
        self.assertEqual(response.context['page'].paginator.count, 2)
        self.assertEqual(TimeSlot.objects.all().count(), 4)

    def test_new_release_different_phase(self):
        create_release('Release B', True, self.development)
        self.client.login(username='bob', password='bob')
        response = self.client.get(self.listing_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(TimeSlot.objects.all().count(), 2)

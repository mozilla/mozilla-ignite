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


class WebcastTestBase(TestCase):
    """Tests for the ``TimeSlot`` mechanics"""

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
            user = user if user else create_user('u%s' % i)
            yield create_submission(title='Submission %s' % i,
                                    created_by=user, phase=phase,
                                    is_winner=are_winners)

    def book_submissions(self, submission_list, release, **kwargs):
        for submission in submission_list:
            create_timeslot(release, is_booked=True, submission=submission,
                            **kwargs)


class WebcastTest(WebcastTestBase):

    def setUp(self):
        self.initial_data = setup_ideation_phase(**setup_ignite_challenge())
        self.ideation = self.initial_data['ideation_phase']
        self.development = self.initial_data['dev_phase']
        super(WebcastTest, self).setUp()
        self.submission_list = self.generate_submissions(2, self.ideation,
                                                         user=self.profile,
                                                         are_winners=True)
        self.release = create_release('Release', True, self.ideation)

    def test_webcast_list(self):
        """Test the archive of webcast submissions"""
        self.book_submissions(self.submission_list, self.release)
        response = self.client.get(reverse('webcast:object_list'))
        self.assertEqual(response.context['page'].paginator.count, 2)

    def test_webcast_upcoming(self):
        """Test the upcoming webcasts"""
        past = datetime.utcnow() - timedelta(hours=1)
        self.book_submissions(self.submission_list, self.release,
                              start_date=past, end_date=past)
        response = self.client.get(reverse('webcast:upcoming'))
        self.assertEqual(response.context['page'].paginator.count, 0)

    def test_webcast_mine_protected(self):
        """Test the user upcoming webcasts"""
        self.book_submissions(self.submission_list, self.release)
        # user has only one winning submission
        response = self.client.get(reverse('webcast:upcoming_mine'))
        self.assertRedirectsLogin(response)

    def test_webcast_mine(self):
        """Test the user upcoming webcasts"""
        self.book_submissions(self.submission_list, self.release)
        self.client.login(username='bob', password='bob')
        response = self.client.get(reverse('webcast:upcoming_mine'))
        self.assertEqual(len(response.context['object_list']), 2)

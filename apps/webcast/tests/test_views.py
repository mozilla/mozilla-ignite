import test_utils

from datetime import datetime, timedelta

from challenges.models import (Submission, Phase, Challenge, Category,
                               Project)
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from timeslot.models import TimeSlot, Release
from timeslot.tests.fixtures import (create_project, create_challenge,
                                     create_phase, create_user, create_release,
                                     create_category, create_submission)


class WebcastTest(test_utils.TestCase):
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
        for model in [Submission, Phase, Challenge, Category, Project,
                      TimeSlot, User, Release]:
            model.objects.all().delete()

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

    def generate_timeslots(self, total):
        """Create a number of ``TimeSlots``"""
        release = create_release('Release', True)
        return [self.create_timeslot(release) for i in range(total)]

    def generate_winning_submissions(self, total):
        """Helper to generate a list of winning submissions"""
        data = {'is_winner': True}
        submission_list = []
        for i in range(total):
            profile = create_user('bob%s' % i)
            submission_list.append(create_submission('Submission %s' % i,
                                                     profile, self.ideation,
                                                     extra_data=data))
        return submission_list

    def test_webcast_list(self):
        """Test the archive of webcast submissions"""
        # create winning submissions
        submission_list = self.generate_winning_submissions(self.SUBMISSIONS)
        webcast_url = reverse('webcast:object_list')
        release = create_release('Release', True)
        # book the winning submissions
        for i, submission in enumerate(submission_list, start=1):
            t_data = {'submission': submission,
                      'is_booked': True}
            timeslot = self.create_timeslot(release, extra_data=t_data)
            response = self.client.get(webcast_url)
            page = response.context['page']
            self.assertEqual(page.paginator.count, i)
        # webcast in the past should be listed as well
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow() - timedelta(days=30)
        for timeslot in TimeSlot.objects.all():
            timeslot.start_date = start_date
            timeslot.end_date = end_date
            timeslot.save()
            response = self.client.get(webcast_url)
            page = response.context['page']
            self.assertEqual(page.paginator.count, self.SUBMISSIONS)

    def test_webcast_upcoming(self):
        """Test the upcoming webcasts"""
        # create winning submissions
        submission_list = self.generate_winning_submissions(self.SUBMISSIONS)
        webcast_url = reverse('webcast:upcoming')
        release = create_release('Release', True)
        # book the winning submissions in the future
        for i, submission in enumerate(submission_list, start=1):
            t_data = {'submission': submission,
                      'is_booked': True}
            timeslot = self.create_timeslot(release, extra_data=t_data)
            response = self.client.get(webcast_url)
            self.assertEqual(response.status_code, 200)
            page = response.context['page']
            self.assertEqual(page.paginator.count, i)
        # webcast in the past should NOT be listed
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow() - timedelta(days=30)
        for i, timeslot in enumerate(TimeSlot.objects.filter(is_booked=True),
                                     start=1):
            timeslot.start_date = start_date
            timeslot.end_date = end_date
            timeslot.save()
            response = self.client.get(webcast_url)
            page = response.context['page']
            self.assertEqual(page.paginator.count, (self.SUBMISSIONS - i))

    def test_webcast_mine(self):
        """Test the user upcoming webcasts"""
        # generate winning submissions
        submission_list = self.generate_winning_submissions(self.SUBMISSIONS)
        release = create_release('Release', True)
        # book all the winning submissions
        for i, submission in enumerate(submission_list, start=1):
            t_data = {'submission': submission,
                      'is_booked': True}
            timeslot = self.create_timeslot(release, extra_data=t_data)
        # user has only one winning submission
        webcast_url = reverse('webcast:upcoming_mine')
        response = self.client.get(webcast_url)
        login_url = reverse('login')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(login_url in response['Location'])
        self.client.login(username='bob1', password='bob1')
        response = self.client.get(webcast_url)
        self.assertEqual(response.status_code, 200)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 1)

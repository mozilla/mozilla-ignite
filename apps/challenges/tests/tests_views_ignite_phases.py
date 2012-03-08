import test_utils

from datetime import datetime
from dateutil.relativedelta import relativedelta

from challenges.models import (Submission, Phase, Challenge, Category,
                               Project)
from challenges.tests.test_views import BLANK_EXTERNALS
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from timeslot.models import TimeSlot
from timeslot.tests.fixtures import (create_project, create_challenge,
                                     create_phase, create_user,
                                     create_category, create_submission,
                                     create_phase_round)


class SubmissionPhasesTest(test_utils.TestCase):
    """Test for the submissions for ignite"""

    def setUp(self):
        """Actions to be performed at the beginning of each test"""
        # setup ignite challenge
        self.project = create_project(settings.IGNITE_PROJECT_SLUG)
        self.challenge = create_challenge(settings.IGNITE_CHALLENGE_SLUG,
                                          self.project)
        self.now = datetime.utcnow()
        self.delta = relativedelta(days=30)
        self.past = self.now - self.delta
        self.future = self.now + self.delta
        # create the Ideation and Development phases
        idea_data = {'order': 1, 'start_date': self.past, 'end_date': self.now}
        self.ideation = create_phase(settings.IGNITE_IDEATION_NAME,
                                     self.challenge, idea_data)
        dev_data = {'order': 2, 'start_date': self.now, 'end_date': self.future}
        self.development = create_phase(settings.IGNITE_DEVELOPMENT_NAME,
                                        self.challenge, dev_data)
        self.category = create_category('miscellaneous');
        self.url = reverse('create_entry')

    def tearDown(self):
        """Actions to be performed at the end of each test"""
        for model in [Submission, Phase, Challenge, Category, Project,
                      TimeSlot, User]:
            model.objects.all().delete()

    def set_ideation(self):
        """Helper to set the site in ``Ideation`` phase"""
        self.ideation.start_date = self.now
        self.ideation.end_date = self.future
        self.ideation.save()
        self.development.start_date = self.future
        self.development.end_date = self.future + self.delta
        self.development.save()

    def set_development(self):
        """Helper to set the site in ``Develop`` phase"""
        self.ideation.start_date = self.past
        self.ideation.end_date = self.now - relativedelta(minutes=1)
        self.ideation.save()
        self.development.start_date = self.now
        self.development.end_date = self.future
        self.development.save()

    def test_ideation_phase_anon_submission(self):
        """Tests a submission made to the ideation phase"""
        self.set_ideation()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        login_url = reverse('login')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(login_url in response['Location'])
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(login_url in response['Location'])

    def test_ideation_phase_submission(self):
        """Creates a submission on the ideation phase with the minimum
        data possible"""
        self.set_ideation()
        name = 'bob'
        profile = create_user(name)
        self.client.login(username=name, password=name)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = {
            'category': self.category.id,
            'title': 'My amazing submission',
            'brief_description': 'This is amazing',
            'description': 'Explanation of why this is amazing',
            'is_draft': False,
            }
        data.update(BLANK_EXTERNALS)
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('entries_all'))
        submission_list = Submission.objects.all()
        self.assertEqual(len(submission_list), 1)
        submission = submission_list[0]
        self.assertEqual(submission.phase, self.ideation)
        self.assertFalse(self.ideation.current_round)
        self.assertFalse(submission.phase_round)

    def test_development_phase_submission(self):
        """Creates a submission on the development phase with
        the minimum data possible"""
        self.set_development()
        data = {
            'start_date': self.now,
            'end_date': self.future,
            }
        phase_round = create_phase_round('Round A', self.development, data)
        name = 'bob'
        profile = create_user(name)
        self.client.login(username=name, password=name)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = {
            'category': self.category.id,
            'title': 'My amazing submission',
            'brief_description': 'This is amazing',
            'description': 'Explanation of why this is amazing',
            'is_draft': False,
            }
        data.update(BLANK_EXTERNALS)
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('entries_all'))
        submission_list = Submission.objects.all()
        self.assertEqual(len(submission_list), 1)
        submission = submission_list[0]
        self.assertEqual(submission.phase, self.development)
        self.assertEqual(phase_round, self.development.current_round)
        self.assertEqual(phase_round, submission.phase_round)

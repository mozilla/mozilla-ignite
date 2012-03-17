from datetime import datetime

from awards.models import JudgeAllowance, SubmissionAward
from challenges.models import (Project, Phase, Submission, Challenge, Category,
                               PhaseRound)
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from test_utils import TestCase
from timeslot.tests.fixtures import (create_user, create_phase, create_project,
                                     create_challenge, create_submission,
                                     create_judge)


class AwardAmountTest(TestCase):

    def setUp(self):
        self.judge = create_judge('bob')
        # setup ignite challenge
        self.project = create_project(settings.IGNITE_PROJECT_SLUG)
        self.challenge = create_challenge(settings.IGNITE_CHALLENGE_SLUG,
                                          self.project)
        self.now = datetime.utcnow()
        self.delta = relativedelta(days=30)
        self.past = self.now - self.delta
        self.future = self.now + self.delta
        # create the Ideation and Development phases
        idea_data = {'order': 1, 'start_date': self.now, 'end_date': self.now}
        self.ideation = create_phase(settings.IGNITE_IDEATION_NAME,
                                     self.challenge, idea_data)
        dev_data = {'order': 2, 'start_date': self.now, 'end_date': self.now}
        self.development = create_phase(settings.IGNITE_DEVELOPMENT_NAME,
                                        self.challenge, dev_data)
        self.user = create_user('alex')
        self.submission = create_submission('a-submission', self.user,
                                            self.ideation)
        self.award_url = reverse('awards:award', args=[self.submission.id])
        self.login_url = reverse('login')

    def tearDown(self):
        for model in [Submission, Phase, Challenge, Category, Project,
                      User, PhaseRound]:
            model.objects.all().delete()

    def create_allowance(self, **kwargs):
        defaults = {
            'amount': 10000,
            'judge': self.judge,
            'phase': self.ideation,
            }
        if kwargs:
            defaults.update(kwargs)
        return JudgeAllowance.objects.create(**defaults)


    def test_award_fail_get_request(self):
        response = self.client.get(self.award_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.login_url in response['Location'])

    def test_award_anon_request(self):
        data = {'amount': 100}
        response = self.client.post(self.award_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.login_url in response['Location'])

    def test_authenticated_request_not_judge(self):
        self.client.login(username='alex', password='alex')
        data = {'amount': 100}
        response = self.client.post(self.award_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.login_url in response['Location'])

    def test_judge_request_not_allowance(self):
        self.client.login(username='bob', password='bob')
        data = {'amount': 100}
        response = self.client.post(self.award_url, data)
        self.assertEqual(response.status_code, 404)

    def test_judge_allocation_non_qualifying_submission(self):
        self.client.login(username='bob', password='bob')
        self.create_allowance()
        data = {'amount': 100}
        response = self.client.post(self.award_url, data)
        self.assertEqual(response.status_code, 404)

    def test_judge_valid_allocation(self):
        self.client.login(username='bob', password='bob')
        self.submission.is_winner = True
        self.submission.save()
        self.create_allowance()
        data = {'amount': 100}
        response = self.client.post(self.award_url, data, follow=True)
        for item in list(response.context['messages']):
            self.assertEqual(item.tags, 'success')
        self.assertRedirects(response, self.submission.get_absolute_url())

    def test_judge_overfound(self):
        self.client.login(username='bob', password='bob')
        self.submission.is_winner = True
        self.submission.save()
        self.create_allowance()
        data = {'amount': 6000}
        response = self.client.post(self.award_url, data, follow=True)
        self.assertRedirects(response, self.submission.get_absolute_url())
        for item in list(response.context['messages']):
            self.assertEqual(item.tags, 'success')
        other_submission = create_submission('other-submission', self.user,
                                             self.ideation, {'is_winner': True})
        other_url = reverse('awards:award', args=[other_submission.id])
        response = self.client.post(other_url, data, follow=True)
        self.assertRedirects(response, other_submission.get_absolute_url())
        self.assertTrue('messages' in response.context)
        for item in list(response.context['messages']):
            self.assertEqual(item.tags, 'error')

    def test_judge_invalid_submission(self):
        self.client.login(username='bob', password='bob')
        self.submission.is_winner = True
        self.submission.save()
        self.create_allowance()
        data = {'amount': 'INVALID'}
        response = self.client.post(self.award_url, data, follow=True)
        self.assertRedirects(response, self.submission.get_absolute_url())
        for item in list(response.context['messages']):
            self.assertEqual(item.tags, 'error')

from datetime import datetime

from awards.models import JudgeAllowance, SubmissionAward, Award
from challenges.models import Submission
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from test_utils import TestCase
from challenges.tests.fixtures.ignite_fixtures import (setup_ignite_challenge,
                                                       teardown_ignite_challenge,
                                                       setup_ideation_phase,
                                                       setup_development_phase,
                                                       create_submission,
                                                       create_user, create_judge)

class AwardAmountTest(TestCase):

    def setUp(self):
        self.initial_data = setup_ideation_phase(is_open=False,
                                                 **setup_ignite_challenge())
        self.ideation = self.initial_data['ideation_phase']
        self.development = self.initial_data['dev_phase']
        self.judge = create_judge('bob')
        self.user = create_user('alex')
        self.submission = create_submission(created_by=self.user,
                                            phase=self.ideation,
                                            is_winner=False)
        self.award_url = reverse('awards:award', args=[self.submission.id])
        self.phase_award = Award.objects.create(phase=self.ideation,
                                                amount=10000)

    def tearDown(self):
        teardown_ignite_challenge()
        for model in [JudgeAllowance, SubmissionAward, Award, Submission,
                      User]:
            model.objects.all().delete()

    def assertRedirectsLogin(self, response):
        login_url = reverse('login')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(login_url in response['Location'])

    def create_allowance(self, **kwargs):
        defaults = {
            'amount': 10000,
            'judge': self.judge,
            'award': self.phase_award,
            }
        if kwargs:
            defaults.update(kwargs)
        return JudgeAllowance.objects.create(**defaults)

    def test_award_fail_get_request(self):
        response = self.client.get(self.award_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirectsLogin(response)

    def test_award_anon_request(self):
        data = {'amount': 100}
        response = self.client.post(self.award_url, data)
        self.assertRedirectsLogin(response)

    def test_authenticated_request_not_judge(self):
        self.client.login(username='alex', password='alex')
        data = {'amount': 100}
        response = self.client.post(self.award_url, data)
        self.assertRedirectsLogin(response)

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
        other_submission = create_submission(title='other-submission',
                                             created_by=self.user,
                                             phase=self.ideation,
                                             is_winner= True)
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

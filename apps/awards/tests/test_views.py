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
from challenges.views import get_award_context


class AwardAmountBaseTest(TestCase):

    def setUp(self):
        self.judge = create_judge('bob')
        self.user = create_user('alex')

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

    def create_phase_award(self, **kwargs):
        defaults = {
            'phase': self.ideation,
            'amount': 10000,
            'status': Award.RELEASED,
            }
        if kwargs:
            defaults.update(kwargs)
        return Award.objects.create(**defaults)


class AwardAmountIdeationClosedTest(AwardAmountBaseTest):

    def setUp(self):
        super(AwardAmountIdeationClosedTest, self).setUp()
        self.initial_data = setup_ideation_phase(is_open=False,
                                                 **setup_ignite_challenge())
        self.ideation = self.initial_data['ideation_phase']
        self.development = self.initial_data['dev_phase']
        self.submission = create_submission(created_by=self.user,
                                            phase=self.ideation,
                                            is_winner=False)
        self.award_url = reverse('awards:award', args=[self.submission.id])
        self.phase_award = self.create_phase_award(phase=self.ideation)

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

    def test_judge_draft_submission(self):
        self.client.login(username='bob', password='bob')
        self.submission.is_winner = True
        self.submission.is_draft = True
        self.submission.save()
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

    def test_non_judge_award_context(self):
        # Mock the middleware that adds the is_judge flag
        self.user.user.is_judge = False
        context = get_award_context(self.submission, self.user.user)
        self.assertFalse(context)

    def test_judge_no_allowance_award_context(self):
        # Mock the middleware that adds the is_judge flag
        self.judge.user.is_judge = True
        context = get_award_context(self.submission, self.judge.user)
        self.assertFalse(context)

    def test_judge_initial_allowance_non_gren_lit_submission(self):
        self.create_allowance()
        self.judge.user.is_judge = True
        # Mock the middleware that adds the is_judge flag
        context = get_award_context(self.submission, self.judge.user)
        self.assertFalse(context['award'])
        self.assertFalse(context['award_form'])
        assert context['allowance'], 'Missing Allowance'

    def test_judge_initial_allowance(self):
        self.submission.is_winner = True
        self.submission.save()
        self.create_allowance()
        self.judge.user.is_judge = True
        # Mock the middleware that adds the is_judge flag
        context = get_award_context(self.submission, self.judge.user)
        self.assertFalse(context['award'])
        assert context['award_form'], 'Missing Form'
        assert context['award_form']['amount'], 'Missing Field'
        assert context['allowance'], 'Missing Allowance'



class AwardDevelopmentOpenPhaseTests(AwardAmountBaseTest):

    def setUp(self):
        super(AwardDevelopmentOpenPhaseTests, self).setUp()
        self.initial_data = setup_development_phase(**setup_ignite_challenge())
        self.ideation = self.initial_data['ideation_phase']
        self.development = self.initial_data['dev_phase']
        self.round_a = self.initial_data['round_a']
        self.submission = create_submission(created_by=self.user,
                                            phase=self.development,
                                            phase_round=self.round_a,
                                            is_winner=False)
        self.award_url = reverse('awards:award', args=[self.submission.id])
        self.phase_award = self.create_phase_award(phase=self.development,
                                                   phase_round=self.round_a)

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

    def test_judge_request_award_not_released(self):
        self.client.login(username='bob', password='bob')
        self.create_allowance()
        self.phase_award.status = Award.PENDING
        self.phase_award.save()
        data = {'amount': 100}
        response = self.client.post(self.award_url, data)
        self.assertEqual(response.status_code, 404)

    def test_judge_allocation_non_qualifying_submission(self):
        self.client.login(username='bob', password='bob')
        self.create_allowance()
        data = {'amount': 100}
        response = self.client.post(self.award_url, data)
        self.assertEqual(response.status_code, 404)

    def test_judge_draft_submission(self):
        self.client.login(username='bob', password='bob')
        self.submission.is_winner = True
        self.submission.is_draft = True
        self.submission.save()
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
                                             phase=self.development,
                                             phase_round=self.round_a,
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


class InvalidAwardsTests(AwardAmountBaseTest):

    def setUp(self):
        super(InvalidAwardsTests, self).setUp()
        self.initial_data = setup_development_phase(**setup_ignite_challenge())
        self.ideation = self.initial_data['ideation_phase']
        self.development = self.initial_data['dev_phase']
        self.round_a = self.initial_data['round_a']
        self.submission = create_submission(created_by=self.user,
                                            phase=self.ideation,
                                            is_winner=True)
        self.award_url = reverse('awards:award', args=[self.submission.id])
        self.phase_award = self.create_phase_award(phase=self.development)

    def test_invalid_award_phase(self):
        self.client.login(username='bob', password='bob')
        self.create_allowance()
        data = {'amount': 100}
        response = self.client.post(self.award_url, data)
        self.assertEqual(response.status_code, 404)

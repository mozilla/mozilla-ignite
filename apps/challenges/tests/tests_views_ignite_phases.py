from datetime import datetime

from challenges.models import Submission, SubmissionParent
from challenges.tests.fixtures.ignite_fixtures import (setup_ignite_challenge,
                                                       teardown_ignite_challenge,
                                                       setup_ideation_phase,
                                                       setup_development_phase,
                                                       create_user)
from challenges.tests.test_views import BLANK_EXTERNALS
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from test_utils import TestCase


class SubmissionPhasesBaseTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'category': self.initial_data['category'].id,
            'title': 'This is full of awesomeness',
            'brief_description': 'Short description',
            'description': 'A bit longer description',
            'is_draft': False,
            'terms_and_conditions': True,
            }
        self.profile = create_user('bob')
        self.url = reverse('create_entry')

    def tearDown(self):
        teardown_ignite_challenge()
        for model in [SubmissionParent, Submission, User]:
            model.objects.all().delete()

    def assertRedirectsLogin(self, response):
        login_url = reverse('login')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(login_url in response['Location'])


class SubmissionIdeationPhaseTests(SubmissionPhasesBaseTest):

    def setUp(self):
        self.initial_data = setup_ideation_phase(**setup_ignite_challenge())
        super(SubmissionIdeationPhaseTests, self).setUp()

    def test_ideation_phase_anon_submission(self):
        response = self.client.get(self.url)
        self.assertRedirectsLogin(response)
        response = self.client.post(self.url, {})
        self.assertRedirectsLogin(response)

    def test_ideation_phase_valid_submission(self):
        """Creates a submission on the ideation phase with the minimum
        data possible"""
        self.client.login(username='bob', password='bob')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.valid_data.update(BLANK_EXTERNALS)
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, reverse('entries_all'))
        submission = Submission.objects.get()
        self.assertEqual(submission.phase, self.initial_data['ideation_phase'])
        self.assertFalse(submission.phase_round)
        assert submission.parent, "Parent missing"

    def test_ideation_phase_non_accepted_tnc(self):
        self.client.login(username='bob', password='bob')
        self.valid_data.update(BLANK_EXTERNALS)
        self.valid_data['terms_and_conditions'] = False
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Submission.objects.all().count(), 0)


class SubmissionIdeationClosedPhaseTests(SubmissionPhasesBaseTest):

    def setUp(self):
        self.initial_data = setup_ideation_phase(is_open=False,
                                                 **setup_ignite_challenge())
        super(SubmissionIdeationClosedPhaseTests, self).setUp()

    def test_development_phase_anon_submission(self):
        response = self.client.get(self.url)
        self.assertRedirectsLogin(response)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 403)

    def test_development_phase_submission_page(self):
        self.client.login(username='bob', password='bob')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_development_phase_submission_post(self):
        self.client.login(username='bob', password='bob')
        self.valid_data.update(BLANK_EXTERNALS)
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 403)


class SubmissionDevelopmentOpenPhaseTests(SubmissionPhasesBaseTest):
    def setUp(self):
        self.initial_data = setup_development_phase(**setup_ignite_challenge())
        super(SubmissionDevelopmentOpenPhaseTests, self).setUp()

    def test_development_phase_anon_submission(self):
        response = self.client.get(self.url)
        self.assertRedirectsLogin(response)
        response = self.client.post(self.url, {})
        self.assertRedirectsLogin(response)

    def test_development_phase_submission(self):
        """Creates a submission on the development phase with
        the minimum data possible"""
        self.client.login(username='bob', password='bob')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.valid_data.update(BLANK_EXTERNALS)
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, reverse('entries_all'))
        submission = Submission.objects.get()
        self.assertEqual(submission.phase, self.initial_data['dev_phase'])
        self.assertEqual(submission.phase_round, self.initial_data['round_a'])
        assert submission.parent, "Parent missing"

    def test_development_phase_non_accepted_tnc(self):
        self.client.login(username='bob', password='bob')
        self.valid_data.update(BLANK_EXTERNALS)
        self.valid_data['terms_and_conditions'] = False
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Submission.objects.all().count(), 0)


class SubmissionDevelopmentClosedRoundTests(SubmissionPhasesBaseTest):
    def setUp(self):
        self.initial_data = setup_development_phase(is_round_open=False,
                                                    **setup_ignite_challenge())
        super(SubmissionDevelopmentClosedRoundTests, self).setUp()

    def test_development_phase_anon_submission(self):
        response = self.client.get(self.url)
        self.assertRedirectsLogin(response)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 403)

    def test_development_phase_submission_page(self):
        self.client.login(username='bob', password='bob')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_development_phase_submission_post(self):
        self.client.login(username='bob', password='bob')
        self.valid_data.update(BLANK_EXTERNALS)
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 403)

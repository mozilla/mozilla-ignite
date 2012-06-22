from datetime import datetime

from challenges.forms import (EntryForm, NewEntryForm, DevelopmentEntryForm,
                              NewDevelopmentEntryForm)
from challenges.models import Submission, SubmissionParent
from challenges.tests.fixtures.ignite_fixtures import (setup_ignite_challenge,
                                                       teardown_ignite_challenge,
                                                       setup_ideation_phase,
                                                       setup_development_phase,
                                                       create_submission,
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
            'life_improvements': 'A lot of improvements',
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

    def test_ideation_phase_form(self):
        self.client.login(username='bob', password='bob')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], NewEntryForm))

    def test_ideation_edit_form(self):
        submission = create_submission(created_by=self.profile,
                                       phase=self.initial_data['ideation_phase'])
        self.client.login(username='bob', password='bob')
        response = self.client.get(reverse('entry_edit', args=[submission.id,]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], EntryForm))

    def test_ideation_save_edit(self):
        submission = create_submission(created_by=self.profile,
                                       phase=self.initial_data['ideation_phase'])
        self.client.login(username='bob', password='bob')
        self.valid_data.update(BLANK_EXTERNALS)
        del self.valid_data['terms_and_conditions']
        response = self.client.post(reverse('entry_edit', args=[submission.id,]),
                                    self.valid_data, follow=True)
        self.assertRedirects(response, submission.get_absolute_url())
        self.assertTrue('messages' in response.context)
        for item in list(response.context['messages']):
            self.assertEqual(item.tags, 'success')


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

    def test_ideation_phase_form(self):
        self.client.login(username='bob', password='bob')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_ideation_edit_form(self):
        submission = create_submission(created_by=self.profile,
                                       phase=self.initial_data['ideation_phase'])
        self.client.login(username='bob', password='bob')
        response = self.client.get(reverse('entry_edit', args=[submission.id,]))
        self.assertEqual(response.status_code, 200)

    def test_ideation_save_edit_failed(self):
        submission = create_submission(created_by=self.profile,
                                       phase=self.initial_data['ideation_phase'])
        self.client.login(username='bob', password='bob')
        self.valid_data.update(BLANK_EXTERNALS)
        del self.valid_data['terms_and_conditions']
        response = self.client.post(reverse('entry_edit', args=[submission.id,]),
                                    self.valid_data, follow=True)
        self.assertEqual(response.status_code, 403)


class SubmissionDevelopmentOpenPhaseTests(SubmissionPhasesBaseTest):
    def setUp(self):
        self.initial_data = setup_development_phase(**setup_ignite_challenge())
        super(SubmissionDevelopmentOpenPhaseTests, self).setUp()
        self.valid_data.update({'repository_url': 'http://mozilla.com'})

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

    def test_development_phase_form(self):
        self.client.login(username='bob', password='bob')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'],
                                   NewDevelopmentEntryForm))

    def test_development_edit_form(self):
        submission = create_submission(created_by=self.profile,
                                       phase=self.initial_data['ideation_phase'])
        self.client.login(username='bob', password='bob')
        response = self.client.get(reverse('entry_edit', args=[submission.id,]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], DevelopmentEntryForm))

    def test_development_save_edit(self):
        submission = create_submission(created_by=self.profile,
                                       phase=self.initial_data['ideation_phase'])
        self.client.login(username='bob', password='bob')
        self.valid_data.update(BLANK_EXTERNALS)
        del self.valid_data['terms_and_conditions']
        response = self.client.post(reverse('entry_edit', args=[submission.id,]),
                                    self.valid_data, follow=True)
        self.assertRedirects(response, submission.get_absolute_url())
        self.assertTrue('messages' in response.context)
        for item in list(response.context['messages']):
            self.assertEqual(item.tags, 'success')
        parent = SubmissionParent.objects.get()
        version_list = parent.submissionversion_set.all()
        self.assertEqual(len(version_list), 1)
        self.assertEqual(version_list[0].submission, submission)
        self.assertEqual(parent.submission.phase,
                         self.initial_data['dev_phase'])
        self.assertEqual(parent.submission.phase_round,
                         self.initial_data['round_a'])


class SubmissionDevelopmentClosedRoundTests(SubmissionPhasesBaseTest):
    def setUp(self):
        self.initial_data = setup_development_phase(is_round_open=False,
                                                    **setup_ignite_challenge())
        super(SubmissionDevelopmentClosedRoundTests, self).setUp()
        self.valid_data.update({'repository_url': 'http://mozilla.com'})

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

    def test_development_phase_form(self):
        self.client.login(username='bob', password='bob')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'],
                                   NewDevelopmentEntryForm))

    def test_development_edit_form(self):
        submission = create_submission(created_by=self.profile,
                                       phase=self.initial_data['ideation_phase'])
        self.client.login(username='bob', password='bob')
        response = self.client.get(reverse('entry_edit', args=[submission.id,]))
        self.assertEqual(response.status_code, 200)

    def test_development_save_edit_failure(self):
        submission = create_submission(created_by=self.profile,
                                       phase=self.initial_data['ideation_phase'])
        self.client.login(username='bob', password='bob')
        self.valid_data.update(BLANK_EXTERNALS)
        del self.valid_data['terms_and_conditions']
        response = self.client.post(reverse('entry_edit', args=[submission.id,]),
                                    self.valid_data, follow=True)
        self.assertEqual(response.status_code, 403)

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
from search.forms import CustomFacetedSearchForm
from test_utils import TestCase

class SearchTest(TestCase):

    def setUp(self):
        self.profile = create_user('bob')
        self.url = reverse('create_entry', args=['ideas'])
        self.initial_data = setup_development_phase(**setup_ignite_challenge())
        self.ideation = self.initial_data['ideation_phase']
        self.development = self.initial_data['dev_phase']
        self.submission_kwargs = {
            'created_by': self.profile,
            'phase': self.ideation,
            'is_winner': True
            }
        self.submission_a = create_submission(title='ping',
                                              **self.submission_kwargs)
        self.submission_b = create_submission(title='pong',
                                              **self.submission_kwargs)
        self.search_url = reverse('search:search')

    def tearDown(self):
        teardown_ignite_challenge()
        for model in [SubmissionParent, Submission, User]:
            model.objects.all().delete()

    def test_search_get(self):
        response = self.client.get(self.search_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'],
                                   CustomFacetedSearchForm))
        self.assertEqual(response.context['page'].paginator.count, 0)

    def test_search_title(self):
        response = self.client.get(self.search_url+ '?q=ping')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'].paginator.count, 1)

    def test_search_capitalization(self):
        response = self.client.get(self.search_url+ '?q=PING')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'].paginator.count, 1)

    def test_different_phase_search(self):
        """Archive a submission and search again"""
        submission_a_fork = create_submission(title='Brand new',
                                              with_parent=False,
                                              **self.submission_kwargs)
        self.submission_a.parent.update_version(submission_a_fork)
        response = self.client.get(self.search_url+ '?q=ping')
        self.assertEqual(response.context['page'].paginator.count, 0)
        response = self.client.get(self.search_url+ '?q=brand')
        self.assertEqual(response.context['page'].paginator.count, 1)


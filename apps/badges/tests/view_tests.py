from badges.models import SubmissionBadge
from badges.tests.base_tests import BadgesBaseTest
from django.core.urlresolvers import reverse
from timeslot.tests.fixtures import create_user, create_submission


class BadgesSubmissionTest(BadgesBaseTest):

    def setUp(self):
        # Ignite fixtures are setup on the BadgesBaseTest
        super(BadgesSubmissionTest, self).setUp()
        self.badge_a = self.create_badge()
        self.badge_b = self.create_badge(body='Award')
        self.user = create_user('bob')
        self.submission = create_submission('Hello', self.user, self.ideation)

    def test_submission_badges(self):
        """Test the badges awarded in the Submission page"""
        data = {
            'submission': self.submission,
            'badge': self.badge_a
            }
        entry = SubmissionBadge.objects.create(**data)
        self.assertTrue(entry.is_published)
        url = reverse('entry_show', kwargs={'entry_id': self.submission.id,
                                            'phase': 'ideas'})
        response = self.client.get(url)
        self.assertEqual(len(response.context['badge_list']), 1)

    def test_hidden_submission_badges(self):
        """Test the hidden badges are not shown on the Submission page"""
        data = {
            'submission': self.submission,
            'badge': self.badge_a,
            'is_published': False,
            }
        SubmissionBadge.objects.create(**data)
        url = reverse('entry_show', kwargs={'entry_id': self.submission.id,
                                            'phase': 'ideas'})
        response = self.client.get(url)
        self.assertEqual(len(response.context['badge_list']), 0)

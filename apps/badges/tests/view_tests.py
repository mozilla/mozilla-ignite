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
        """Test the badges awarded in the submission"""
        data = {
            'submission': self.submission,
            'badge': self.badge_a
            }
        SubmissionBadge.objects.create(**data)
        url = reverse('entry_show', args=[self.submission.id])
        response = self.client.get(url)
        self.assertEqual(len(response.context['badge_list']), 1)

from badges.models import Badge
from badges.tests.base_tests import BadgesBaseTest
from challenges.models import Submission
from timeslot.tests.fixtures import create_user, create_submission


class TimeSlotModelTest(BadgesBaseTest):

    def create_badge(self):
        """Creates a ``Badge`` with the less possible data"""
        data = {
            'badge_type': Badge.GREEN_LIT,
            }
        badge = Badge.objects.create(**data)
        assert badge.id, "Failure creating the badge"

    def create_submission_badge(self):
        """Creates a ``SubmissionBadge``"""
        data = {
            'badge_type': Badge.GREEN_LIT,
            'body': 'On the badge',
            }
        badge = Badge.objects.create(**data)
        bob = create_user('bob')
        submission = create_submission('Lorem Ipsum', bob, self.ideation)
        submission_badge = Submission.objects.create(badge=badge,
                                                     submission=submission)
        assert submission_badge.id, "Submission Badge creation failed"
        self.assertEqual(submission_badge.text, 'On the badge')
        submission_badge.body = 'Set on the submission'
        self.assertEqual(submission_badge.text, 'Set on the submission')


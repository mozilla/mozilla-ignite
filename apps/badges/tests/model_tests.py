import test_utils

from datetime import datetime

from badges.models import Badge, SubmissionBadge
from challenges.models import (Submission, Phase, Challenge, Category,
                               Project)
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from timeslot.tests.fixtures import (create_project, create_challenge,
                                     create_phase, create_user, create_release,
                                     create_category, create_submission)


class TimeSlotModelTest(test_utils.TestCase):

    def setUp(self):
        """Actions to be performed at the beginning of each test"""
        # setup ignite challenge
        self.project = create_project(settings.IGNITE_PROJECT_SLUG)
        self.challenge = create_challenge(settings.IGNITE_CHALLENGE_SLUG,
                                          self.project)
        now = datetime.utcnow()
        past = now - relativedelta(days=30)
        future = now + relativedelta(days=30)
        # create the Ideation and Development phases
        idea_data = {'order': 1, 'start_date': past, 'end_date': now}
        self.ideation = create_phase(settings.IGNITE_IDEATION_NAME,
                                     self.challenge, idea_data)
        dev_data = {'order': 2, 'start_date': now, 'end_date': future}
        self.development = create_phase(settings.IGNITE_DEVELOPMENT_NAME,
                                        self.challenge, dev_data)

    def tearDown(self):
        """Actions to be performed at the end of each test"""
        for model in [Submission, Phase, Challenge, Category, Project,
                      User]:
            model.objects.all().delete()

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


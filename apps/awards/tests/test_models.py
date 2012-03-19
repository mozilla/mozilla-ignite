from awards.models import JudgeAllowance, SubmissionAward, Award
from challenges.models import Project, Phase, Submission
from django.contrib.auth.models import User
from test_utils import TestCase
from timeslot.tests.fixtures import (create_user, create_phase, create_project,
                                     create_challenge, create_submission)


class JudgeAllowanceTest(TestCase):

    def setUp(self):
        self.judge = create_user('bob')
        project = create_project('A project')
        challenge = create_challenge('A challenge', project)
        self.phase = create_phase('A phase', challenge)
        self.user = create_user('alex')
        self.submission = create_submission('A submission', self.user,
                                            self.phase)
        self.phase_award = Award.objects.create(phase=self.phase,
                                                amount=10000)

    def tearDown(self):
        for model in [Award, Project, Phase, Submission, User]:
            model.objects.all().delete()

    def award(self, submission, amount, allowance):
        data = {
            'judge_allowance': allowance,
            'amount': amount,
            'submission': submission,
            }
        return SubmissionAward.objects.create(**data)

    def create_allowance(self, **kwargs):
        defaults = {
            'amount': 10000,
            'award': self.phase_award,
            'judge': self.judge,
            }
        if kwargs:
            defaults.update(kwargs)
        return JudgeAllowance.objects.create(**defaults)

    def test_create_allowance(self):
        """Create the ``JudgeAllowance`` with the minimum required data"""
        data = {
            'amount': 10000,
            'judge': self.judge,
            'award': self.phase_award,
            }
        allowance = JudgeAllowance.objects.create(**data)
        assert allowance.id, "Failed to create JudgeAllowance"

    def test_amount_free(self):
        allowance = self.create_allowance()
        amount_used = allowance.get_amount_used(self.submission)
        self.assertEqual(amount_used, 0)

    def test_update_amount_submision(self):
        allowance = self.create_allowance()
        self.award(self.submission, 4000, allowance)
        amount_used = allowance.get_amount_used()
        self.assertEqual(amount_used, 4000)
        amount_used = allowance.get_amount_used(self.submission)
        self.assertEqual(amount_used, 0)

    def test_amount_allocated_new_submission(self):
        allowance = self.create_allowance()
        self.award(self.submission, 4000, allowance)
        other = create_submission('Other Submission', self.user, self.phase)
        self.award(other, 400, allowance)
        new_sub = create_submission('New Submission', self.user, self.phase)
        amount_used = allowance.get_amount_used(new_sub)
        self.assertEqual(amount_used, 4400)

    def test_amount_used(self):
        allowance = self.create_allowance()
        amount_used = allowance.get_amount_used(self.submission)

    def test_valid_award(self):
        allowance = self.create_allowance()
        self.assertTrue(allowance.can_award(10000, self.submission))

    def test_valid_upgrade_award(self):
        allowance = self.create_allowance()
        self.award(self.submission, 9000, allowance)
        self.assertTrue(allowance.can_award(10000, self.submission))

    def test_not_enough_allowance(self):
        allowance = self.create_allowance()
        self.award(self.submission, 9000, allowance)
        other = create_submission('Other submission', self.user, self.phase)
        self.assertFalse(allowance.can_award(10000, other))

    def test_allocate_successful(self):
        allowance = self.create_allowance()
        self.assertTrue(allowance.allocate(9000, self.submission))

    def test_allocate_upgrade(self):
        allowance = self.create_allowance()
        self.assertTrue(allowance.allocate(9000, self.submission))
        self.assertTrue(allowance.allocate(10000, self.submission))

    def test_allocate_upgrade_failure(self):
        allowance = self.create_allowance()
        self.assertTrue(allowance.allocate(9000, self.submission))
        self.assertFalse(allowance.allocate(11000, self.submission))

    def test_allocate_other_full(self):
        allowance = self.create_allowance()
        self.assertTrue(allowance.allocate(9000, self.submission))
        other = create_submission('Other Submission', self.user, self.phase)
        self.assertTrue(allowance.allocate(1000, other))

    def test_allocate_other_failure(self):
        allowance = self.create_allowance()
        self.assertTrue(allowance.allocate(9000, self.submission))
        other = create_submission('Other Submission', self.user, self.phase)
        self.assertFalse(allowance.allocate(1001, other))


class SubmissionAwardTest(TestCase):

    def setUp(self):
        self.judge = create_user('bob')
        project = create_project('A project')
        challenge = create_challenge('A challenge', project)
        self.phase = create_phase('A phase', challenge)
        self.user = create_user('alex')
        self.submission = create_submission('A submission', self.user,
                                            self.phase)
        self.phase_award = Award.objects.create(phase=self.phase,
                                                amount=10000)

    def tearDown(self):
        for model in [Award, Project, Phase, User]:
            model.objects.all().delete()

    def create_allowance(self, **kwargs):
        defaults = {
            'amount': 10000,
            'judge': self.judge,
            'award': self.phase_award,
            }
        if kwargs:
            defaults.update(kwargs)
        return JudgeAllowance.objects.create(**defaults)

    def test_create_submission_award(self):
        """Create the SubmissionAward with the minimum required data"""
        allowance = self.create_allowance()
        data = {
            'judge_allowance': allowance,
            'amount': 10000,
            'submission': self.submission,
            }
        award = SubmissionAward.objects.create(**data)
        assert award.id, "Failed to create SubmissionAward"

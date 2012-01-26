from collections import defaultdict

from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase
from django.core.cache import cache

from challenges.tests.test_judging import judging_setup
from challenges.management.commands.assign import (get_judge_profiles,
                                                   get_submissions,
                                                   get_assignments)
from challenges.models import Submission, Judgement, JudgeAssignment


class AssignmentTest(TestCase):
    
    def assertEvenAssignment(self, assignments):
        counts = defaultdict(lambda: 0)
        for assignment in assignments:
            counts[assignment.judge] += 1
        # No judge has more than one submission more than any other
        self.assertTrue(max(counts.values()) - min(counts.values()) <= 1)
    
    def setUp(self):
        judging_setup(create_criteria=False, submission_count=5)
        self.judging_permission = Permission.objects.get(
                                      codename='judge_submission')
        charlie = User.objects.get(username='charlie')
        charlie.user_permissions.add(self.judging_permission)
        cache.clear()
    
    def test_get_judges(self):
        self.assertEqual(set([j.user.username for j in get_judge_profiles()]),
                         set(['alex', 'charlie']))
    
    def test_get_judges_superuser(self):
        """Test superusers aren't automatically returned as judges."""
        User.objects.filter(username='bob').update(is_superuser=True)
        self.assertEqual(set([j.user.username for j in get_judge_profiles()]),
                         set(['alex', 'charlie']))
    
    def test_judge_group(self):
        """Test that judges with permission through a group are included."""
        judges = Group.objects.create(name='Judges')
        judges.permissions.add(self.judging_permission)
        for user in User.objects.filter(username__in=['alex', 'charlie']):
            user.user_permissions.clear()
            if user.username == 'charlie':
                user.groups.add(judges)
        self.assertEqual(set([j.user.username for j in get_judge_profiles()]),
                         set(['charlie']))
    
    def test_submissions(self):
        self.assertEqual(len(get_submissions()), 5)
    
    def test_no_judged_submissions(self):
        """Test judged submissions aren't included for assignment."""
        alex_profile = User.objects.get(username='alex').get_profile()
        submission = Submission.objects.get(title='Submission 3')
        Judgement.objects.create(judge=alex_profile, submission=submission,
                                 notes='Blah')
        self.assertEqual(set(s.title for s in get_submissions()),
                         set(['Submission %d' % n for n in [1, 2, 4, 5]]))
    
    def test_no_assigned_submissions(self):
        """Test assigned submissions aren't included for assignment."""
        alex_profile = User.objects.get(username='alex').get_profile()
        submission = Submission.objects.get(title='Submission 2')
        JudgeAssignment.objects.create(submission=submission,
                                       judge=alex_profile)
        self.assertEqual(set(s.title for s in get_submissions()),
                         set(['Submission %d' % n for n in [1, 3, 4, 5]]))
    
    def test_no_assigned_judged_submissions(self):
        """Test previously-assigned, judged submissions."""
        alex_profile = User.objects.get(username='alex').get_profile()
        submission_a = Submission.objects.get(title='Submission 4')
        submission_b = Submission.objects.get(title='Submission 2')
        Judgement.objects.create(judge=alex_profile, submission=submission_a,
                                 notes='Blah')
        JudgeAssignment.objects.create(submission=submission_b,
                                       judge=alex_profile)
        self.assertEqual(set(s.title for s in get_submissions()),
                         set(['Submission %d' % n for n in [1, 3, 5]]))
    
    def test_assignments(self):
        assignments = get_assignments(submissions=get_submissions(),
                                      judge_profiles=get_judge_profiles(),
                                      commit=False)
        self.assertEvenAssignment(assignments)
        # Check nothing has been saved
        self.assertEqual(JudgeAssignment.objects.count(), 0)
    
    def test_assignment_commit(self):
        assignments = get_assignments(submissions=get_submissions(),
                                      judge_profiles=get_judge_profiles(),
                                      commit=True)
        self.assertEvenAssignment(assignments)
        self.assertEqual(JudgeAssignment.objects.count(),
                         Submission.objects.count())

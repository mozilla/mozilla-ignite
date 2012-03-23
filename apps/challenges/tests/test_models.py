from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase
from mock import Mock, patch

from projects.models import Project
from challenges.models import (Challenge, Submission, Phase, Category,
                              ExclusionFlag, Judgement, JudgingCriterion,
                              PhaseCriterion, PhaseRound, SubmissionParent,
                              SubmissionVersion, SubmissionHelp)
from challenges.tests.fixtures import (challenge_setup, create_submissions,
                                       create_users, challenge_teardown)
from challenges.tests.test_base import TestPhasesBase
from timeslot.tests.fixtures import (create_user, create_submission,
                                      create_phase_round)
from ignite.tests.decorators import ignite_skip


def _create_project_and_challenge():
    """Create and return a sample project with a sample challenge."""
    project = Project.objects.create(name='Project', slug='project',
                                          allow_participation=True)
    end_date = datetime.utcnow() + timedelta(days=365)
    challenge = Challenge.objects.create(title='Challenge',
                                              slug='challenge',
                                              end_date=end_date,
                                              project=project)
    return project, challenge


class PermalinkTest(TestCase):
    
    def setUp(self):
        self.project, self.challenge = _create_project_and_challenge()
    
    @ignite_skip
    def test_permalink(self):
        self.assertEqual(self.challenge.get_absolute_url(),
                         '/project/challenges/challenge/')
    
    def tearDown(self):
        for model in [Challenge, Project]:
            model.objects.all().delete()


class SingleChallengePermalinkTest(TestCase):
    
    urls = 'challenges.tests.single_challenge_urls'
    
    def setUp(self):
        self.project, self.challenge = _create_project_and_challenge()
    
    def test_single_challenge_permalink(self):
        """Test permalink generation on an Ignite-style one-challenge site."""
        self.assertEqual(self.challenge.get_absolute_url(), '/')
    
    def tearDown(self):
        for model in [Challenge, Project]:
            model.objects.all().delete()


class EntriesToLive(TestCase):
    
    def setUp(self):
        self.project = Project.objects.create(
            name=u'A project for a test',
            allow_participation=True
        )
        self.challenge = Challenge.objects.create(
            title=u'Testing my submissions',
            end_date=u'2020-11-30 12:23:28',
            project=self.project,
            moderate=True
        )
        self.phase = Phase.objects.create(
            name=u'Phase 1', challenge=self.challenge, order=1
        )
        self.user = User.objects.create_user('bob', 'bob@example.com', 'bob')
        self.category = Category.objects.create(name='Misc', slug='misc')
        self.submission = Submission.objects.create(
            title=u'A submission to test',
            description=u'<h3>Testing bleach</h3>',
            phase=self.phase,
            created_by=self.user.get_profile(),
            category=self.category
        )
        self.submission_marked = Submission.objects.create(
            title=u'A submission with markdown',
            description=u'I **really** like cake',
            phase=self.phase,
            created_by=self.user.get_profile(),
            category=self.category
        )

    def test_phase_unicode(self):
        """Test the string representation of a phase."""
        self.assertEqual(unicode(self.phase),
                         u'Phase 1 (Testing my submissions)')
    
    def test_bleach_clearning(self):
        """
        Check that we're stripping out bad content - <h3> isn't in our 
        allowed list
        """
        self.assertEqual(self.submission.description_html,
                         '&lt;h3&gt;Testing bleach&lt;/h3&gt;')

    def test_markdown_conversion(self):
        """
        Check that we're converting markdown before outputting
        """
        self.assertEqual(self.submission_marked.description_html,
            '<p>I <strong>really</strong> like cake</p>')


class CategoryManager(TestCase):
    
    def setUp(self):
        self.project = Project.objects.create(
            name=u'Test Project',
            allow_participation=True
        )
        self.challenge = Challenge.objects.create(
            title=u'Testing categories',
            end_date=u'2020-11-30 12:23:28',
            description=u'Blah',
            project=self.project,
            moderate=False
        )
        self.phase = Phase.objects.create(
            name=u'Phase 1',
            order=1,
            challenge=self.challenge
        )
        self.user = User.objects.create_user('bob', 'bob@bob.com', 'bob')
        self.c1 = Category.objects.create(
            name=u'Testing',
            slug=u'testing'
        )
        self.c2 = Category.objects.create(
            name=u'Ross',
            slug=u'ross'
        )

    def test_initial_return(self):
        """
        Test that with no categories containing submissions returns nothing
        """
        self.assertEqual(Category.objects.get_active_categories(), False)

    def test_results_after_submission(self):
        """
        Test that we return only categories with submissions in
        """
        Submission.objects.create(
            title=u'Category',
            brief_description=u'Blah',
            description=u'Foot',
            phase=self.phase,
            created_by=self.user.get_profile(),
            category=self.c1
        )
        
        self.cats = Category.objects.get_active_categories()
        self.assertEqual(len(self.cats), 1)

    def tearDown(self):
        for model in [Challenge, Project, Phase, User, Category, Submission]:
            model.objects.all().delete()



class Phases(TestCase):

    def setUp(self):
        self.project, self.challenge = _create_project_and_challenge()

        self.p1 = Phase.objects.create(
            name=u'Phase 1',
            order=1,
            challenge=self.challenge,
            start_date = datetime.utcnow(),
            end_date = datetime.utcnow() + relativedelta( months = +1 )
        )
        self.p2 = Phase.objects.create(
            name=u'Phase 2',
            order=2,
            challenge=self.challenge,
            start_date = datetime.utcnow() + relativedelta( months = +2 ),
            end_date = datetime.utcnow() + relativedelta( months = +3 )
        )

    def test_get_current_open(self):
       current = Phase.objects.get_current_phase(self.challenge.slug)
       self.assertEqual(current.name, 'Phase 1')

    def tearDown(self):
        for model in [Challenge, Project, Phase]:
            model.objects.all().delete()


class Criteria(TestCase):
    
    def test_value_range(self):
        c = JudgingCriterion(question='How awesome is this idea?', max_value=5)
        self.assertEqual(list(c.range), [0, 1, 2, 3, 4, 5])
    
    def test_good_range(self):
        c = JudgingCriterion(question='How awesome is this idea?', max_value=5)
        c.clean()
    
    def test_bad_range(self):
        c = JudgingCriterion(question='How awesome is this idea?',
                             max_value=-5)
        self.assertRaises(ValidationError, c.clean)
    
    def test_single_unit_range(self):
        c = JudgingCriterion(question='How awesome is this idea?', max_value=0)
        # A range of 0 to 0 is theoretically valid, but you can't weight it
        self.assertRaises(ValidationError, c.clean)


class JudgementScoring(TestCase):
    
    def setUp(self):
        challenge_setup()
        user = User.objects.create_user('bob', 'bob@example.com', 'bob')
        create_submissions(1)
        
        self.phase = Phase.objects.get()
        self.submission = Submission.objects.get()
        self.judge = user.get_profile()
    
    def test_equal_weighting(self):
        for i in range(4):
            c = JudgingCriterion.objects.create(question='Question %d' % i,
                                                max_value=10)
            PhaseCriterion.objects.create(phase=self.phase, criterion=c,
                                          weight=25)
        judgement = Judgement.objects.create(submission=self.submission,
                                             judge=self.judge)
        ratings = [3, 5, 7, 8]
        for criterion, rating in zip(JudgingCriterion.objects.all(), ratings):
            judgement.answers.create(criterion=criterion, rating=rating)
        
        self.assertTrue(judgement.complete)
        self.assertEqual(judgement.get_score(), Decimal('57.5'))
    
    def test_unequal_weighting(self):
        for i, weight in zip(range(4), [15, 25, 25, 35]):  # Total: 100
            c = JudgingCriterion.objects.create(question='Question %d' % i,
                                                max_value=10)
            PhaseCriterion.objects.create(phase=self.phase, criterion=c,
                                          weight=weight)
        judgement = Judgement.objects.create(submission=self.submission,
                                             judge=self.judge)
        ratings = [3, 5, 7, 8]
        criteria = JudgingCriterion.objects.all().order_by('question')
        for criterion, rating in zip(criteria, ratings):
            judgement.answers.create(criterion=criterion, rating=rating)
        
        self.assertTrue(judgement.complete)
        # 3 * 1.5 + 5 * 2.5 + 7 * 2.5 + 8 * 3.5
        self.assertEqual(judgement.get_score(), Decimal('62.5'))
    
    def test_incomplete_judgement(self):
        """Test that scoring an incomplete judgement raises an error."""
        for i in range(4):
            c = JudgingCriterion.objects.create(question='Question %d' % i,
                                                max_value=10)
            PhaseCriterion.objects.create(phase=self.phase, criterion=c,
                                          weight=25)
        judgement = Judgement.objects.create(submission=self.submission,
                                             judge=self.judge)
        ratings = [3, 5, 7]
        # Only three ratings, so zip will ignore the last criterion
        for criterion, rating in zip(JudgingCriterion.objects.all(), ratings):
            judgement.answers.create(criterion=criterion, rating=rating)
        
        self.assertFalse(judgement.complete)
        self.assertRaises(Judgement.Incomplete, judgement.get_score)
    
    def test_no_criteria(self):
        """Test behaviour when there are no criteria."""
        judgement = Judgement.objects.create(submission=self.submission,
                                             judge=self.judge)
        self.assertTrue(judgement.complete)
        self.assertEqual(judgement.get_score(), Decimal('0.00'))


class TestSubmissions(TestCase):

    def setUp(self):
        challenge_setup()
        create_submissions(3)
        self.phase = Phase.objects.get()
        cache.clear()

    def test_no_exclusions(self):
        self.assertEqual(Submission.objects.eligible(self.phase).count(), 3)

    def test_exclusion(self):
        excluded = Submission.objects.all()[0]
        ExclusionFlag.objects.create(submission=excluded, notes='Blah blah')
        self.assertEqual(Submission.objects.eligible(self.phase).count(), 2)


class TestSubmissionsMultiplePhases(TestPhasesBase):

    def setUp(self):
        super(TestSubmissionsMultiplePhases, self).setUp()
        self.user = create_user('bob')
        self.round_a = create_phase_round('A', self.development)
        self.round_b = create_phase_round('B', self.development)

    def test_exclude_submission_phases(self):
        for i in range(3):
            create_submission('Submision %s' % i, self.user, self.ideation)
        self.assertEqual(Submission.objects.eligible(self.ideation).count(), 3)
        self.assertEqual(Submission.objects.eligible(self.development).count(), 0)
        self.assertEqual(Submission.objects.count(), 3)

    def test_exclude_submission_rounds(self):
        extra = {'phase_round': self.round_a}
        for i in range(3):
            create_submission('Submision %s' % i, self.user, self.ideation, extra)
        self.assertEqual(Submission.objects.eligible(self.ideation,
                                                     self.round_a).count(), 3)
        self.assertEqual((Submission.objects.eligible(self.ideation,
                                                      self.round_b).count()), 0)

    def test_exclude_submission_version(self):
        i_list = [create_submission('Submision %s' % i,
                                    self.user, self.ideation) for i in range(3)]
        item = i_list[0]
        new_sub = create_submission('Replacement', self.user, self.development,
                                    parent=False)
        self.assertEqual(Submission.objects.count(), 4)
        parent = item.submissionparent_set.all()[0]
        parent.update_version(new_sub)
        self.assertEqual(Submission.objects.eligible(self.ideation).count(), 2)
        self.assertEqual(Submission.objects.eligible(self.development).count(), 1)

    def test_exclude_drafts(self):
        i_list = [create_submission('Submision %s' % i,
                                    self.user, self.ideation) for i in range(3)]
        self.assertEqual(Submission.objects.eligible(self.ideation).count(), 3)
        for item in i_list:
            item.is_draft = True
            item.save()
        self.assertEqual(Submission.objects.eligible(self.ideation).count(), 0)


class DraftSubmissionTest(TestCase):
    
    def setUp(self):
        challenge_setup()
        create_users()
        alex_profile = User.objects.get(username='alex').get_profile()
        create_submissions(5, creator=alex_profile)
        
        self.draft_submission = Submission.objects.all()[0]
        self.draft_submission.is_draft = True
        self.draft_submission.save()
        
        cache.clear()
    
    def test_draft_not_public(self):
        assert self.draft_submission not in Submission.objects.visible()
    
    def test_non_draft_visible(self):
        """Test live submissions are visible to anyone and everyone."""
        alex, bob = [User.objects.get(username=u) for u in ['alex', 'bob']]
        s = Submission.objects.all()[3]
        assert s in Submission.objects.visible()
        for user in [alex, bob]:
            assert s in Submission.objects.visible(user=user)
            assert user.has_perm('challenges.view_submission', obj=s)
    
    def test_draft_not_visible_to_user(self):
        bob = User.objects.get(username='bob')
        assert self.draft_submission not in Submission.objects.visible(user=bob)
        assert not bob.has_perm('challenges.view_submission',
                                obj=self.draft_submission)
    
    def test_draft_visible_to_author(self):
        alex = User.objects.get(username='alex')
        assert self.draft_submission in Submission.objects.visible(user=alex)
        assert alex.has_perm('challenges.view_submission',
                             obj=self.draft_submission)


class PhaseRoundTest(TestCase):

    def setUp(self):
        challenge_setup()
        self.phase = Phase.objects.all()[0]

    def tearDown(self):
        for model in [Challenge, Project, Phase, User, Category, Submission,
                      PhaseRound]:
            model.objects.all().delete()

    def test_create_phase(self):
        data = {
            'name': 'Round A',
            'phase': self.phase,
            'start_date': datetime.utcnow(),
            'end_date': datetime.utcnow() + relativedelta(hours=1),
            }
        phase = PhaseRound.objects.create(**data)
        assert phase.slug, 'Slug missing on: %s' % phase
        self.assertTrue(phase.is_active)


class SubmissionParentTest(TestCase):

    def setUp(self):
        challenge_setup()
        profile_list = create_users()
        self.phase = Phase.objects.all()[0]
        self.created_by = profile_list[0]
        self.category = Category.objects.all()[0]

    def create_submission(self, **kwargs):
        defaults = {
            'title': 'Title',
            'brief_description': 'A submission',
            'description': 'A really good submission',
            'phase': self.phase,
            'created_by': self.created_by,
            'category': self.category,
            }
        if kwargs:
            defaults.update(kwargs)
        return Submission.objects.create(**defaults)

    def tearDown(self):
        for model in [Challenge, Project, Phase, User, Category, Submission,
                      SubmissionParent]:
            model.objects.all().delete()

    def test_parent_creation(self):
        """Create a ``SubmissionParent`` with the less possible data"""
        submission = self.create_submission(title='a')
        parent = SubmissionParent.objects.create(submission=submission)
        assert parent.id, "SubmissionParent creation failure"
        self.assertEqual(parent.status, SubmissionParent.ACTIVE)
        self.assertEqual(parent.slug, submission.id)
        self.assertEqual(parent.name, submission.title)

    def test_parent_visibility(self):
        submission = self.create_submission(title='a')
        parent = SubmissionParent.objects.create(submission=submission)
        self.assertEqual(Submission.objects.visible().count(), 1)
        parent.status = SubmissionParent.INACTIVE
        parent.save()
        self.assertEqual(Submission.objects.visible().count(), 0)

    def test_submission_without_parent(self):
        submission = self.create_submission(title='a')
        self.assertEqual(Submission.objects.visible().count(), 0)


class SubmissionParentVersioningTest(TestCase):

    def setUp(self):
        challenge_setup()
        profile_list = create_users()
        self.phase = Phase.objects.all()[0]
        self.created_by = profile_list[0]
        self.category = Category.objects.all()[0]
        self.submission_a = self.create_submission(title='a')
        self.submission_b = self.create_submission(title='b')
        self.parent = SubmissionParent.objects.create(submission=self.submission_a)

    def create_submission(self, **kwargs):
        defaults = {
            'title': 'Title',
            'brief_description': 'A submission',
            'description': 'A really good submission',
            'phase': self.phase,
            'created_by': self.created_by,
            'category': self.category,
            }
        if kwargs:
            defaults.update(kwargs)
        return Submission.objects.create(**defaults)

    def test_update_parent_history(self):
        self.parent.update_version(self.submission_b)
        submission_versions = SubmissionVersion.objects.all()
        self.assertEqual(len(submission_versions), 1)
        submission_version = submission_versions[0]
        self.assertEqual(submission_version.submission, self.submission_a)
        self.assertEqual(self.parent.submission, self.submission_b)

    def test_update_parent_values(self):
        self.parent.update_version(self.submission_b)
        self.assertEqual(self.parent.submission, self.submission_b)
        self.assertEqual(self.parent.slug, self.submission_a.id)
        self.assertEqual(self.parent.name, self.submission_b.title)

    def test_visible_submission(self):
        """Test a versioned Submission is not visible on all listing"""
        self.parent.update_version(self.submission_b)
        assert self.submission_a not in Submission.objects.visible()
        assert self.submission_a in Submission.objects.all()


class SubmissionHelpTest(TestCase):
    def setUp(self):
        challenge_setup()
        profile_list = create_users()
        self.phase = Phase.objects.all()[0]
        self.created_by = profile_list[0]
        self.category = Category.objects.all()[0]
        create_submissions(1, self.phase, self.created_by)
        self.submission_a = Submission.objects.get()
        self.parent = self.submission_a.parent

    def tearDown(self):
        challenge_teardown()
        for model in [SubmissionHelp]:
            model.objects.all().delete()

    def create_submission_help(self):
        submission_help = SubmissionHelp.objects.create(parent=self.parent,
                                                        notes='Help Wanted')
        assert submission_help.created, "SubmissionHelp failed"
        self.assertEqual(submission_help.status, SubmissionHelp.DRAFT)

    def submission_help_manager(self):
        submission_help = SubmissionHelp.objects.create(parent=self.parent,
                                                        notes='Help Wanted')
        self.assertEqual(SubmissionHelp.objects.get_active().count(), 0)
        submission_help.status = SubmissionHelp.PUBLISHED
        submission_help.save()
        self.assertEqual(SubmissionHelp.objects.get_active().count(), 1)

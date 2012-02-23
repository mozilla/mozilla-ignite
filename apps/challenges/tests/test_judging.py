from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from nose.tools import assert_equal, with_setup
from test_utils import TestCase

from challenges.forms import JudgingForm
from challenges.models import Phase, Submission, JudgingCriterion, Judgement, \
                              JudgingAnswer, JudgeAssignment, PhaseCriterion
from challenges.tests.fixtures import (challenge_setup, challenge_teardown,
                                       create_submissions, create_users)
from challenges.tests.test_views import MessageTestCase
from ignite.tests.decorators import ignite_only


def judging_setup(create_criteria=True, submission_count=1):
    challenge_setup()
    if create_criteria:
        questions = ['How %s is this idea?' % adjective
                     for adjective in ['awesome', 'sane', 'badass']]
        for question in questions:
            criterion = JudgingCriterion.objects.create(question=question)
            PhaseCriterion.objects.create(phase=Phase.objects.get(),
                                          criterion=criterion)
    
    create_users()
    submission_type = ContentType.objects.get_for_model(Submission)
    judge_permission, _ = Permission.objects.get_or_create(
                                        codename='judge_submission',
                                        content_type=submission_type)
    alex = User.objects.get(username='alex')
    alex.user_permissions.add(judge_permission)
    
    create_submissions(submission_count, creator=alex.get_profile())


class JudgingFormTest(TestCase):
    
    def setUp(self):
        judging_setup()
    
    def test_judging_form(self):
        """Test a new instance of the judging form."""
        criteria = Phase.objects.get().judgement_criteria.all()
        # Quick sanity check that the criteria exist
        assert len(criteria) > 0
        
        form = JudgingForm(criteria=criteria)
        expected_keys = set(['notes'] + ['criterion_%s' % c.pk for c in criteria])
        assert_equal(set(form.fields.keys()), expected_keys)
        assert_equal(form.initial, {})
    
    def test_judging_form_with_data(self):
        """Test an instance of the judging form with bound criteria."""
        judge = User.objects.get(username='alex').get_profile()
        submission = Submission.objects.get()
        
        judgement = Judgement.objects.create(submission=Submission.objects.get(),
                                             judge=judge,
                                             notes='Something something notes.')
        phase_criteria = submission.phase.judgement_criteria.all()
        for criterion, rating in zip(phase_criteria, [3, 5, 7]):
            JudgingAnswer.objects.create(criterion=criterion, judgement=judgement,
                                         rating=rating)
        
        form = JudgingForm(instance=judgement, criteria=phase_criteria)
        assert all('criterion_%s' % c.pk in form.initial for c in phase_criteria)
    
    def test_rating_out_of_range(self):
        criteria = Phase.objects.get().judgement_criteria.all()
        # Quick sanity check
        assert len(criteria) == 3
        
        criteria_keys = ['criterion_%s' % c.pk for c in criteria]
        data = {'notes': 'Blah', criteria_keys[0]: 5, criteria_keys[1]: 5,
                criteria_keys[2]: 15}
        
        form = JudgingForm(data, criteria=criteria)
        assert_equal(form.errors.keys(), [criteria_keys[2]])
    
    def test_save_without_criteria(self):
        """Test saving a new judgement with an empty list of criteria."""
        
        judge_profile = User.objects.get(username='alex').get_profile()
        submission = Submission.objects.get()
        
        new_judgement = Judgement(judge=judge_profile, submission=submission)
        form = JudgingForm({'notes': 'Blah'}, criteria=[],
                           instance=new_judgement)
        
        assert form.is_valid()
        judgement = form.save()
        
        assert judgement is new_judgement
        
        assert_equal(Judgement.objects.count(), 1)
        assert_equal(Judgement.objects.get().notes, 'Blah')
        assert_equal(JudgingAnswer.objects.count(), 0)
    
    def test_save_form_create(self):
        """Test saving a new judgement."""
        criteria = Phase.objects.get().judgement_criteria.all()
        # Quick sanity check
        assert len(criteria) == 3
        
        judge_profile = User.objects.get(username='alex').get_profile()
        submission = Submission.objects.get()
        
        criteria_keys = ['criterion_%s' % c.pk for c in criteria]
        data = {'notes': 'Blah', criteria_keys[0]: 3, criteria_keys[1]: 5,
                criteria_keys[2]: 7}
        
        new_judgement = Judgement(judge=judge_profile, submission=submission)
        form = JudgingForm(data, criteria=criteria, instance=new_judgement)
        
        assert form.is_valid()
        judgement = form.save()
        
        assert_equal(Judgement.objects.count(), 1)
        assert_equal(Judgement.objects.get().notes, 'Blah')
        answers = JudgingAnswer.objects.filter(judgement=judgement)
        for criterion, rating in zip(criteria, [3, 5, 7]):
            assert_equal(answers.get(criterion=criterion).rating, rating)
    
    def test_save_form_update(self):
        """Test updating an existing judgement."""
        
        criteria = Phase.objects.get().judgement_criteria.all()
        # Quick sanity check
        assert len(criteria) == 3
        
        judge_profile = User.objects.get(username='alex').get_profile()
        submission = Submission.objects.get()
        
        judgement = Judgement.objects.create(submission=submission,
                                             judge=judge_profile,
                                             notes='Old notes')
        
        for criterion in criteria:
            JudgingAnswer.objects.create(judgement=judgement,
                                         criterion=criterion,
                                         rating=1)
        
        criteria_keys = ['criterion_%s' % c.pk for c in criteria]
        data = {'notes': 'Blah', criteria_keys[0]: 3, criteria_keys[1]: 5,
                criteria_keys[2]: 7}
        
        form = JudgingForm(data, criteria=criteria, instance=judgement)
        assert form.is_valid()
        form.save()
        
        assert_equal(list(judgement.answers.values_list('rating', flat=True)),
                     [3, 5, 7])


class JudgingViewTest(MessageTestCase):
    
    def setUp(self):
        judging_setup()
    
    @ignite_only
    def test_no_judge_form(self):
        """Test the form doesn't show if the user doesn't have permission."""
        submission = Submission.objects.get()
        response = self.client.get(submission.get_absolute_url())
        assert response.context['judging_form'] is None
    
    @ignite_only
    def test_judge_form(self):
        """Test displaying the judge form."""
        submission = Submission.objects.get()
        assert self.client.login(username='alex', password='alex')
        response = self.client.get(submission.get_absolute_url())
        judging_form = response.context['judging_form']
        assert 'notes' in judging_form.fields
        criteria = submission.phase.judgement_criteria.all()
        expected_keys = set(['criterion_%s' % c.pk for c in criteria])
        expected_keys.add('notes')
        self.assertEqual(set(judging_form.fields.keys()), expected_keys)
    
    @ignite_only
    def test_non_eliminated_entry(self):
        """Test that non-eliminated entries are not marked as eliminated."""
        submission = Submission.objects.get()
        assert self.client.login(username='alex', password='alex')
        response = self.client.get(submission.get_absolute_url())
        self.assertEqual(response.context['excluded'], False)
    
    @ignite_only
    def test_eliminated_entry(self):
        """Test that eliminated entries are shown properly."""
        submission = Submission.objects.get()
        submission.exclusionflag_set.create(notes='This entry sucks')
        assert self.client.login(username='alex', password='alex')
        response = self.client.get(submission.get_absolute_url())
        self.assertEqual(response.context['excluded'], True)
    
    @ignite_only
    def test_submit_judge_form(self):
        """Test judging an unjudged submission."""
        submission = Submission.objects.get()
        assert self.client.login(username='alex', password='alex')
        response = self.client.get(submission.get_absolute_url())
        judging_form = response.context['judging_form']
        post_data = {'notes': 'This submission is acceptable to me.'}
        for key in judging_form.fields:
            if key.startswith('criterion_'):
                post_data[key] = '5'
        post_response = self.client.post(submission.get_judging_url(),
                                         data=post_data,
                                         follow=True)
        self.assertRedirects(post_response, reverse('entries_assigned'))
        self.assertSuccessMessage(post_response)
        
        judgement = Judgement.objects.get()
        self.assertEqual(judgement.judge.user.username, 'alex')
        self.assertEqual(judgement.submission, submission)
        for answer in judgement.answers.all():
            self.assertEqual(answer.rating, 5)
    
    @ignite_only
    def test_judge_not_assigned(self):
        """Test behaviour when the current user is not assigned this entry."""
        submission = Submission.objects.get()
        assert self.client.login(username='alex', password='alex')
        response = self.client.get(submission.get_absolute_url())
        assert response.context['judge_assigned'] is False
    
    @ignite_only
    def test_judge_assigned(self):
        """Test behaviour when the current user is assigned this entry."""
        submission = Submission.objects.get()
        user_profile = User.objects.get(username='alex').get_profile()
        JudgeAssignment.objects.create(submission=submission,
                                       judge=user_profile)
        assert self.client.login(username='alex', password='alex')
        response = self.client.get(submission.get_absolute_url())
        assert response.context['judge_assigned'] is True
    
    @ignite_only
    def test_another_judge_assigned(self):
        """Test behaviour when the someone else is assigned this entry."""
        submission = Submission.objects.get()
        user_profile = User.objects.get(username='charlie').get_profile()
        JudgeAssignment.objects.create(submission=submission,
                                       judge=user_profile)
        assert self.client.login(username='alex', password='alex')
        response = self.client.get(submission.get_absolute_url())
        assert response.context['judge_assigned'] is False
    
    @ignite_only
    def test_amend_judgement(self):
        """Test posting the judgement form when a judgement already exists."""
        submission = Submission.objects.get()
        assert self.client.login(username='alex', password='alex')
        judge = User.objects.get(username='alex').get_profile()
        
        judgement = Judgement.objects.create(submission=submission, judge=judge,
                                             notes='Blah blah blah')
        for criterion in submission.phase.judgement_criteria.all():
            JudgingAnswer.objects.create(judgement=judgement,
                                         criterion=criterion, rating=1)
        
        response = self.client.get(submission.get_absolute_url())
        judging_form = response.context['judging_form']
        post_data = {'notes': 'I actually quite like this submission.'}
        ratings = [6, 7, 8]
        for key in judging_form.fields:
            if key.startswith('criterion_'):
                post_data[key] = str(ratings.pop())
        post_response = self.client.post(submission.get_judging_url(),
                                         data=post_data,
                                         follow=True)
        self.assertRedirects(post_response, reverse('entries_assigned'))
        self.assertSuccessMessage(post_response)
        
        new_judgement = Judgement.objects.get()
        self.assertEqual(new_judgement.judge.user.username, 'alex')
        self.assertEqual(new_judgement.submission, submission)
        assert 'quite like' in new_judgement.notes
        ratings = new_judgement.answers.values_list('rating', flat=True)
        self.assertEqual(set(ratings), set([6, 7, 8]))

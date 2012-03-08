from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import User
from django.test import TestCase
from nose.tools import assert_equal

from challenges.models import (Challenge, Submission, Phase, Category,
                              ExclusionFlag, Judgement, JudgingCriterion,
                              PhaseCriterion, PhaseRound, ExternalLink)
from challenges.forms import EntryLinkForm, PhaseRoundAdminForm
from challenges.tests.fixtures import challenge_setup
from projects.models import Project


class NewLinkFormTest(TestCase):
    
    def setUp(self):
        self.tearDown()
    
    def tearDown(self):
        ExternalLink.objects.all().delete()
    
    def test_new_object(self):
        form = EntryLinkForm(data={'name': 'fish', 'url': 'http://example.com/'})
        assert not form.is_blank()
        assert form.is_valid()
        assert not form.errors
    
        form.save()
        link = ExternalLink.objects.get()
        assert_equal(link.name, 'fish')
        assert_equal(link.url, 'http://example.com/')
    
    def test_blank_new_object(self):
        form = EntryLinkForm(data={})
        assert form.is_blank()
        assert form.is_valid()
        assert not form.errors
        
        form.save()
        assert_equal(ExternalLink.objects.count(), 0)
    
    def test_partial_new_object(self):
        form = EntryLinkForm(data={'name': 'foo', 'url': ''})
        assert not form.is_blank()
        assert not form.is_valid()
        assert form.errors


class ExistingLinkFormTest(TestCase):
    
    def setUp(self):
        self.tearDown()
        ExternalLink.objects.create(name='fish', url='http://example.com/')
    
    def tearDown(self):
        ExternalLink.objects.all().delete()
    
    def test_empty_form(self):
        """Test that an empty form triggers a deletion."""
        form = EntryLinkForm(data={}, instance=ExternalLink.objects.get())
        assert form.is_blank()
        assert form.is_valid()
        assert not form.errors
        
        form.save()
        
        assert_equal(ExternalLink.objects.count(), 0)
    
    def test_partial_form(self):
        form = EntryLinkForm(data={'name': 'blah', 'url': ''},
                             instance=ExternalLink.objects.get())
        
        assert not form.is_blank()
        assert not form.is_valid()
        assert form.errors


class PhaseRoundAdminFormTest(TestCase):

    def setUp(self):
        challenge_setup()
        self.phase = Phase.objects.all()[0]
        self.start_date = datetime.utcnow()
        self.end_date = self.phase.start_date + relativedelta(days=30)
        self.half_date = self.phase.start_date + relativedelta(days=15)
        self.delta = relativedelta(days=1)
        # specify start and end date of the Phase to something we
        # can refer to
        self.phase.start_date = self.start_date
        self.phase.end_date = self.end_date
        self.phase.save()

    def tearDown(self):
        for model in [Challenge, Project, Phase, User, Category, Submission]:
            model.objects.all().delete()

    def test_valid_phase(self):
        """Create a valid phase submission from the Phase details"""
        data = {
            'name': 'Round A',
            'phase': self.phase.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            }
        form = PhaseRoundAdminForm(data)
        self.assertTrue(form.is_valid())
        instance = form.save()
        assert instance.id, "PhaseRound wasn't created"
        self.assertEqual(Phase.objects.all().count(), 1)

    def test_round_outside_phase(self):
        """Round dates outside the phase valid dates"""
        data = {
            'name': 'Round A',
            'phase': self.phase.id,
            'start_date': self.phase.start_date - self.delta,
            'end_date': self.phase.end_date,
            }
        form = PhaseRoundAdminForm(data)
        self.assertFalse(form.is_valid())

    def test_rounds_overlaping(self):
        """Test Rounds that overlap"""
        # create valid PhaseRound
        data = {
            'name': 'Round A',
            'phase': self.phase.id,
            'start_date': self.phase.start_date,
            'end_date': self.half_date,
            }
        form = PhaseRoundAdminForm(data)
        self.assertTrue(form.is_valid())
        round_a = form.save()
        assert round_a.id, "PhaseRound wasn't created"
        self.assertEqual(PhaseRound.objects.all().count(), 1)
        # create overlapping phase round
        # overlaping dates
        dates =[
            # wraps the date
            (self.start_date - self.delta, self.half_date + self.delta),
            # is contained in the date
            (self.start_date + self.delta, self.half_date - self.delta),
            # overlaps on the start
            (self.start_date + self.delta, self.end_date),
            # overlaps on the end
            (self.half_date - self.delta, self.end_date),
            ]
        for start, end in dates:
            data = {
                'name': 'Round',
                'phase': self.phase.id,
                'start_date': start,
                'end_date': end,
                }
            form = PhaseRoundAdminForm(data)
            self.assertFalse(form.is_valid())
        self.assertEqual(Phase.objects.all().count(), 1)
        # add new Round with a valid Phase
        data = {
            'name': 'Round B',
            'phase': self.phase.id,
            'start_date': self.half_date + relativedelta(seconds=1),
            'end_date': self.end_date,
            }
        form = PhaseRoundAdminForm(data)
        self.assertTrue(form.is_valid())
        round_b = form.save()
        assert round_b.id, "PhaseRound wasn't created"
        self.assertEqual(PhaseRound.objects.all().count(), 2)

from awards.managers import JudgeAllowanceManager
from challenges.lib import cached_property
from django.db import models
from django.db.models import Sum, Q
from django_extensions.db.fields import CreationDateTimeField
from tower import ugettext_lazy as _


class Award(models.Model):
    """Award for a given ``Phase`` or ``PhaseRound``"""
    PENDING = 1
    RELEASED = 2
    FROZEN = 3
    AWARD_STATUS = (
        (PENDING, _('Pending')),
        (RELEASED, _('Released')),
        (FROZEN, _('Frozen')),
        )
    amount = models.IntegerField(default=0)
    phase = models.ForeignKey('challenges.Phase')
    phase_round = models.ForeignKey('challenges.PhaseRound',
                                    blank=True, null=True)
    status = models.IntegerField(choices=AWARD_STATUS, default=PENDING)

    class Meta:
        unique_together = (('phase', 'phase_round'),)

    def __unicode__(self):
        return u'Allowance of %s on %s' % (self.amount, self.phase)


class JudgeAllowance(models.Model):
    """Allowance for a ``Judge`` on an ``Award``"""
    amount = models.IntegerField(default=0)
    judge = models.ForeignKey('users.Profile')
    award = models.ForeignKey('awards.Award')
    created = CreationDateTimeField()

    # managers
    objects = JudgeAllowanceManager()

    def __unicode__(self):
        return u'Allowance of %s for %s' % (self.amount, self.judge)

    def get_amount_used(self, submission=None):
        """Determines the amount used. If a ``Submission`` is provided
        Will won't take the amount asigned into consideration. Since it could
        be an upgrade/downgrade"""
        amount_used_qs = self.submissionaward_set
        if submission:
            amount_used_qs = amount_used_qs.filter(~Q(submission=submission))
        else:
            amount_used_qs = amount_used_qs.all()
        amount_used = amount_used_qs.aggregate(Sum('amount'))
        amount = amount_used['amount__sum']
        return amount if amount else 0

    @cached_property
    def amount_used(self):
        return self.get_amount_used()

    @cached_property
    def amount_free(self):
        return self.amount - self.amount_used

    def can_award(self, amount_requested, submission):
        """Determines if the amount can be awarded to the submission"""
        amount_available = self.amount - self.get_amount_used(submission)
        return amount_available >= amount_requested and amount_requested > 0

    def allocate(self, amount, submission):
        """Allocates the given amount"""
        if self.can_award(amount, submission):
            instance, created = (SubmissionAward.objects
                                 .get_or_create(judge_allowance=self,
                                                submission=submission))
            instance.amount = amount
            instance.save()
            return True
        return False


class SubmissionAward(models.Model):
    """Money awarded to a ``Submission``"""
    judge_allowance = models.ForeignKey('awards.JudgeAllowance')
    amount = models.IntegerField(default=0)
    submission = models.ForeignKey('challenges.Submission')
    created = CreationDateTimeField()

    class Meta:
        unique_together = (('judge_allowance', 'submission'),)

    def __unicode__(self):
        return u'Award of %s for %s' % (self.amount, self.submission)

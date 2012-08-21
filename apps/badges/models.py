from django.db import models
from django_extensions.db.fields import CreationDateTimeField
from tower import ugettext as _


class Badge(models.Model):
    """``Badges`` to be awarded"""
    GREEN_LIT = "green-lit"
    FUNDED_1 = "funded-1"
    FUNDED_2 = "funded-2"
    FUNDED_3 = "funded-3"
    PEOPLES_CHOICE = "peoples-choice"
    BADGE_CHOICES = (
        (GREEN_LIT, _("Green lit")),
        (FUNDED_1, _("Funded in Round 1")),
        (FUNDED_2, _("Funded in Round 2")),
        (FUNDED_3, _("Funded in Round 3")),
        (PEOPLES_CHOICE, _("People's choice")),
        )
    badge_type = models.CharField(choices=BADGE_CHOICES, max_length=50,
                                  help_text=_('Design to be used with the badge'))
    body = models.CharField(blank=True, max_length=255)

    def __unicode__(self):
        return u'%s (%s)' % (self.body, self.get_badge_type_display())


class SubmissionBadge(models.Model):
    """``Badges`` awarded to ``Submissions``"""
    badge = models.ForeignKey('badges.Badge')
    submission = models.ForeignKey('challenges.Submission')
    body = models.CharField(blank=True, max_length=255)
    is_published = models.BooleanField(default=True)
    created_on = CreationDateTimeField()

    class Meta:
        unique_together = (('badge', 'submission'),)

    def __unicode__(self):
        return u'Badge %s assigned to %s' % (self.badge, self.submission)

    @property
    def text(self):
        return self.body if self.body else self.badge.body

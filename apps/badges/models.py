from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import CreationDateTimeField


class Badge(models.Model):
    """``Badges`` to be awarded"""
    GREEN_LIT = 'green-lit'
    BADGE_CHOICES = (
        (GREEN_LIT, _('Green lit')),
        )
    badge_type = models.CharField(choices=BADGE_CHOICES, max_length=50)
    body = models.CharField(blank=True, max_length=255)

    def __unicode__(self):
        return u'%s: %s' % (self.get_badge_type_display(), self.body)


class SubmissionBadge(models.Model):
    """``Badges`` awarded to ``Submissions``"""
    badge = models.ForeignKey('badges.Badge')
    submission = models.ForeignKey('challenges.Submission')
    body = models.CharField(blank=True, max_length=255)
    created_on = CreationDateTimeField()

    class Meta:
        unique_together = (('badge', 'submission'),)

    @property
    def text(self):
        return self.body if self.body else self.badge.body

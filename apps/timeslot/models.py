from datetime import timedelta, datetime

from django.conf import settings
from django.db import models
from django_extensions.db.fields import AutoSlugField
from timeslot.managers import TimeSlotFreeManager, ReleaseManager
from timeslot.utils import shorten_object


class TimeSlot(models.Model):
    """Defines the ``TimeSlot`` available for booking"""
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    is_booked = models.BooleanField(default=False)
    submission = models.ForeignKey('challenges.Submission', blank=True,
                                   null=True)
    booking_date = models.DateTimeField(blank=True, null=True)
    webcast_url = models.URLField(verify_exists=False, max_length=500,
                                  blank=True)
    release = models.ForeignKey('timeslot.Release')

    # managers
    objects = models.Manager()
    available = TimeSlotFreeManager()

    class Meta:
        ordering = ['start_date', ]

    def __unicode__(self):
        return u'TimeSlot: %s - %s' % (self.start_date, self.end_date)

    @property
    def short_id(self):
        return shorten_object(self)

    def has_expired(self):
        """Determines if this booking has expired"""
        expire_date = self.booking_date + \
            timedelta(seconds=settings.BOOKING_EXPIRATION)
        return any([expire_date < datetime.now(), self.is_booked])


class Release(models.Model):
    """Each ``TimeSlot`` are part of a release"""
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name')
    is_current = models.BooleanField(default=True)

    # managers
    objects = ReleaseManager()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Makes sure we only have a current release"""
        if self.is_current:
            self.__class__.objects.update(is_current=False)
        super(Release, self).save(*args, **kwargs)

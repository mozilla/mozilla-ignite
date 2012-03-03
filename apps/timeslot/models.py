from datetime import timedelta, datetime

from django.conf import settings
from django.db import models
from timeslot.managers import TimeSlotFreeManager
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

    # managers
    objects = models.Manager()
    free = TimeSlotFreeManager()

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

from datetime import timedelta, datetime

from django.conf import settings
from django.db import models
from django_extensions.db.fields import CreationDateTimeField
from timeslot.managers import TimeSlotFreeManager
from timeslot.utils import shorten_object


class TimeSlot(models.Model):
    """Defines the ``TimeSlot`` available for booking"""
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    is_booked = models.BooleanField(default=False)
    # managers
    objects = models.Manager()
    free = TimeSlotFreeManager()

    def __unicode__(self):
        return u'TimeSlot: %s - %s' % (self.start_date, self.end_date)

    @property
    def short_id(self):
        return shorten_object(self)


class Booking(models.Model):
    """Time associated with a submission"""
    timeslot = models.ForeignKey('timeslot.TimeSlot')
    submission = models.ForeignKey('challenges.Submission')
    is_confirmed = models.BooleanField(default=False)
    created = CreationDateTimeField()

    def __unicode__(self):
        return u'Booking for %s' % self.submission

    def has_expired(self):
        """Determines if this booking has expired"""
        expire_date = self.created + timedelta(seconds=settings.BOOKING_EXPIRATION)
        return any([expire_date < datetime.now(), self.is_confirmed])

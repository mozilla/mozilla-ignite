from django.db import models

class TimeSlotFreeManager(models.Manager):
    def get_query_set(self):
        """Makes sure the timeslots are available:
        - They are not booked
        - The release is current
        """
        return super(TimeSlotFreeManager, self).get_query_set().\
            filter(is_booked=False, release__is_current=True)


class ReleaseManager(models.Manager):

    def get_current(self):
        """Returns the active manager"""
        try:
            return self.get(default=True)
        except self.model.DoesNotExist:
            return None

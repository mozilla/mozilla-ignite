from django.db import models

class TimeSlotFreeManager(models.Manager):
    def get_query_set(self):
        return super(TimeSlotFreeManager, self).get_query_set().\
            filter(is_booked=False)

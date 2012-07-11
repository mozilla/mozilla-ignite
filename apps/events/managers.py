from django.db import models
from datetime import datetime


class EventManager(models.Manager):

    def get_featured(self):
        now = datetime.utcnow()
        return self.get_query_set().filter(featured=True, end__gt=now)

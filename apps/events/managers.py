from django.db import models


class EventManager(models.Manager):

    def get_featured(self):
        return self.get_query_set().filter(featured=True)

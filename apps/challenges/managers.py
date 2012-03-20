from django.db import models

class SubmissionHelpManager(models.Manager):

    def get_active(self):
        return self.filter(status=self.model.PUBLISHED)

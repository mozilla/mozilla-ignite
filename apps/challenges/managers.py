from datetime import datetime

from django.db import models
from django.db.models import Q
from django.conf import settings
from innovate.models import BaseModelManager


class PhaseManager(BaseModelManager):

    def get_from_natural_key(self, challenge_slug, phase_name):
        return self.get(challenge__slug=challenge_slug, name=phase_name)

    def get_current_phase(self, slug):
        now = datetime.utcnow()
        try:
            return self.filter(challenge__slug=slug,
                               start_date__lte=now,
                               end_date__gte=now)[0]
        except IndexError:
            return None

    def get_judging_phase(self, slug):
        """Determines the judging ``Phase`` if the end_date is in the past
        or a ``PhaseRound`` has past"""
        now = datetime.utcnow()
        try:
            return self.filter((Q(end_date__lte=now) |
                                Q(phaseround__end_date__lte=now)),
                                challenge__slug=slug).order_by('-end_date')[0]
        except IndexError:
            return None

    def get_ideation_phase(self):
        """Returns the ``Ideation`` phase"""
        try:
            return self.get(challenge__slug=settings.IGNITE_CHALLENGE_SLUG,
                            name=settings.IGNITE_IDEATION_NAME)
        except self.model.DoesNotExist:
            return None

    def get_development_phase(self):
        """Returns the ``Development`` phase"""
        try:
            return self.get(challenge__slug=settings.IGNITE_CHALLENGE_SLUG,
                            name=settings.IGNITE_DEVELOPMENT_NAME)
        except self.model.DoesNotExist:
            return None


class SubmissionHelpManager(models.Manager):

    def get_active(self):
        return self.filter(status=self.model.PUBLISHED)

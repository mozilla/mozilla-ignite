from datetime import datetime

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from innovate.models import BaseModelManager


class SubmissionManager(BaseModelManager):

    def eligible(self, phase, phase_round=None):
        """Return all eligible submissions
        - Not excluded
        - With an entry in the current phase.
        - Submission must be in the current ``SubmissionParent``
        - Is not a draft
        Older submissions when edited will always have an entry in the current
        phase"""
        from challenges.models import SubmissionParent
        qs = {'phase': phase}
        if phase_round:
            qs.update({'phase_round': phase_round})
        return self.filter(exclusionflag__isnull=True, is_draft=False,
                           submissionparent__status=SubmissionParent.ACTIVE,
                           **qs)

    # Note: normally anything mutable wouldn't go into a default, but we can be
    # sure this method doesn't modify the anonymous user
    def visible(self, user=AnonymousUser()):
        """Return all submissions that are visible.
        If a user is provided, return all submissions visible to that user; if
        not, return all submissions visible to the general public."""
        if user.is_superuser:
            return self.current()
        criteria = models.Q(is_draft=False)
        if not user.is_anonymous():
            criteria |= models.Q(created_by__user=user)
        # Return only active submissions
        return self.current().filter(criteria)

    def green_lit(self, phase, phase_round=None):
        """Returns all the ``Submissions`` that have been green-lit.
        Each ``Submission`` belongs to a ``Phase`` or ``PhaseRound``
        hence once it is marked as winner is green-lit for this phase"""
        return self.eligible(phase, phase_round).filter(is_winner=True)

    def current(self):
        """Returns all the ``Submissions`` that are active"""
        from challenges.models import SubmissionParent
        return self.filter(submissionparent__status=SubmissionParent.ACTIVE)


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

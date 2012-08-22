import logging

from django.conf import settings
from django.core.cache import cache
from challenges.models import Phase


class PhaseStatusMiddleware(object):

    def process_view(self, request, *args, **kwargs):
        """Adds the phases with it's status querying the dates on the
        ``Phase`` and ``PhaseRound``"""
        if any(p in request.path for p in settings.MIDDLEWARE_URL_EXCEPTIONS):
            return
        ideation = Phase.objects.get_ideation_phase()
        development = Phase.objects.get_development_phase()
        request.ideation = ideation
        request.development = development
        return


class JudgeMiddleware(object):

    def process_view(self, request, *args, **kwargs):
        """Adds a flag to determine if the user is a judge"""
        if request.user.is_authenticated() and \
            request.user.has_perm('challenges.judge_submission'):
            request.user.is_judge = True
        else:
            request.user.is_judge = False
        return

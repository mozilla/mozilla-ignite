import logging

from django.conf import settings
from django.core.cache import cache
from challenges.models import Phase


class PhaseStatusMiddleware(object):

    def process_view(self, request, *args, **kwargs):
        """Determines when the site ``is_open`` for ``Submissions`` by
        querying the dates on the ``Phase`` and ``PhaseRound``"""
        if any(p in request.path for p in settings.MIDDLEWARE_URL_EXCEPTIONS):
            return
        key = 'IGNITE_PHASE_STATUS'
        if cache.get(key):
            request.phase = cache.get(key)
            return
        phase  = Phase.objects.get_current_phase(settings.IGNITE_CHALLENGE_SLUG)
        defaults = {
            'is_open': False,
            'days_remaining': -1,
            'phase_round': None,
            'id': None,
            'name': None,
            }
        if phase:
            defaults.update({'id': phase.id, 'name': phase.name})
            # Add round values
            if phase.phase_rounds:
                defaults['is_open'] = True if phase.current_round else False
                if phase.current_round:
                    defaults.update({
                        'phase_round': phase.current_round.name,
                        'days_remaining': phase.current_round.days_remaining.days,
                        })
            else:
                # this phase has no rounds
                defaults.update({
                    'is_open': True,
                    'days_remaining': phase.days_remaining.days,
                    })
        cache.set(key, defaults, 60 * 30)  # 30 minutes
        if 'debug_toolbar' in settings.INSTALLED_APPS:
            logging.debug(defaults)
        request.phase = defaults
        return

from challenges.models import Submission, Phase, has_phase_finished
from django.conf import settings

def assigned_submissions_processor(request):
    """Add the number of assigned submissions to the request context."""
    # Avoid any admin, media or debug url
    if any(p in request.path for p in settings.MIDDLEWARE_URL_EXCEPTIONS):
        return {}
    try:
        user = request.user
    except:
        # For some reason, we can't get hold of the user information
        return {}
    # Rf we don't have the phase in the request, we assume it is closed
    is_open = request.phase['is_open'] if hasattr(request, 'phase') else False
    # judging only should happen when the phases are closed
    # only calculate the details when user is a judge
    if is_open or not user.has_perm('challenges.judge_submission'):
        return {}
    profile = user.get_profile()
    # Determine which is the phase that is being Judged at the moment
    phase = Phase.objects.get_judging_phase(settings.IGNITE_CHALLENGE_SLUG)
    if not phase:
        return {}
    qs = {'phase': phase}
    if phase.judging_phase_round:
        qs.update({'phase_round': phase.judging_phase_round})
    # Count the submissions assigned but not judged
    assigned = (Submission.objects
                .filter(judgeassignment__judge=profile, **qs)
                .exclude(judgement__judge=profile))
    return {'assignment_count': assigned.count()}


class ClosedPhase(object):
    """Object that mimicks a closed ``Phase``"""

    @property
    def is_open(self):
        return False

    @property
    def is_closed(self):
        return True


def phases_context_processor(request):
    """Makes the ``Phases`` available in context when templates are rendered"""
    context = {}
    for slug in ['ideation', 'development']:
        if hasattr(request, slug):
            phase = getattr(request, slug)
            context[slug] = phase if phase else ClosedPhase()
    return context

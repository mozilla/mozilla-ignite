from django.conf import settings

from challenges.models import Submission


def assigned_submissions_processor(request):
    """Add the number of assigned submissions to the request context."""
    # Avoid any admin, media or debug url
    # User should be authenticated and be a judge
    if any(p in request.path for p in settings.MIDDLEWARE_URL_EXCEPTIONS) \
        or not request.user.is_authenticated() \
        or not request.user.has_perm('challenges.judge_submission'):
        return {}
    # Judges should have a profile, fail as loud as possible
    # if the judge doesn't have one.
    profile = request.user.get_profile()
    # Submissions assigned to the user that haven't been Scored
    submissions = (Submission.objects.assigned_to_user(profile)
                   .exclude(judgement__judge=profile))
    return {'assignment_count': len(submissions)}


class ClosedPhase(object):
    """Object that mimicks a closed ``Phase``"""

    @property
    def is_open(self):
        return False

    @property
    def is_closed(self):
        return True

    @property
    def has_started(self):
        return False


def phases_context_processor(request):
    """Makes the ``Phases`` available in context when templates are rendered"""
    context = {}
    for slug in ['ideation', 'development']:
        phase = getattr(request, slug) if hasattr(request, slug) else None
        context[slug] = phase if phase else ClosedPhase()
    return context

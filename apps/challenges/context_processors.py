from challenges.models import Submission, has_phase_finished
from django.conf import settings

def assigned_submissions_processor(request):
    """Add the number of assigned submissions to the request context."""
    try:
        user = request.user
    except:
        # For some reason, we can't get hold of the user information
        return {}
    
    if not user.has_perm('challenges.judge_submission'):
        return {}
    profile = user.get_profile()
    
    # Count the submissions assigned but not judged
    assigned = (Submission.objects.filter(judgeassignment__judge=profile)
                                  .exclude(judgement__judge=profile))
    return {'assignment_count': assigned.count()}

def current_phase(request):
    """Add to the context the ``DEVELOPMENT_PHASE``is active
    and if the ``IDEATION_PHASE`` has finished"""
    return {
        'DEVELOPMENT_PHASE': settings.DEVELOPMENT_PHASE,
        'IDEATION_PHASE': has_phase_finished(settings.IGNITE_IDEATION_NAME),
        }

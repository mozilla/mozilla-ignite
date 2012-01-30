from challenges.models import Submission

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

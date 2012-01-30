from challenges.models import JudgeAssignment

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
    assignment_count = JudgeAssignment.objects.filter(judge=profile).count()
    return {'assignment_count': assignment_count}

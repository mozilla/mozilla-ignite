from challenges.models import JudgeAssignment

def assigned_submissions_processor(request):
    """Add the number of assigned submissions to the request context."""
    if not request.user.has_perm('challenges.judge_submission'):
        return {}
    profile = request.user.get_profile()
    assignment_count = JudgeAssignment.objects.filter(judge=profile).count()
    return {'assignment_count': assignment_count}

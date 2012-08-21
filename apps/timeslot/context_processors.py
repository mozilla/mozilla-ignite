from challenges.models import Submission
from timeslot.models import TimeSlot
from django.db.models import Q


def timeslot_notifications(request):
    """Determine the notifications for the timeslot for this user"""
    if request.user.is_authenticated():
        profile = request.user.get_profile()
    booked_qs = (TimeSlot.objects.select_related('submission').
                 filter(submission__created_by=profile, is_booked=True))
    booked_ids = [i.submission.id for i in booked_qs]
    submission_count = (Submission.objects.green_lit().
                        select_related('created_by').
                        filter(~Q(id__in=booked_ids), created_by=profile).
                        count())
    return {'TIMESLOT_NOTIFICATIONS': submission_count}

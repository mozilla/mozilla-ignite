import jingo

from datetime import datetime

from django.contrib.auth.decorators import login_required
from timeslot.models import TimeSlot


@login_required
def upcoming(request, template='webcast/upcoming.html'):
    """Lists the upcoming webcasts for this user"""
    profile = request.user.get_profile()
    upcoming_list = TimeSlot.objects.select_related('submission').\
        filter(submission__created_by=profile, is_booked=True)
    context = {
        'object_list': upcoming_list,
        'profile': profile,
        }
    return jingo.render(request, template, context)


def webcast_list(request, template='webcast/upcoming_all.html'):
    """Lists all webcasts"""
    now = datetime.utcnow()
    upcoming_list = TimeSlot.objects.select_related('submission').\
        filter(is_booked=True, end_date__gte=now)
    context = {
        'object_list': upcoming_list,
        }
    return jingo.render(request, template, context)

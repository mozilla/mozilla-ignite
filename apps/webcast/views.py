import jingo

from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import Http404
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


def webcast_list(request, slug='all', template=None):
    """Lists all webcasts"""
    now = datetime.utcnow()
    filters = {
        'all': {},
        'upcoming': {'end_date__gte': now},
        }
    if not slug in filters:
        raise Http404
    queryset = filters[slug]
    upcoming_list = TimeSlot.objects.select_related('submission').\
        filter(is_booked=True, **queryset)
    context = {
        'object_list': upcoming_list,
        }
    if not template:
        template =  'webcast/webcast_%s.html' % slug
    return jingo.render(request, template, context)

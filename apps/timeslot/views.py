import jingo

from datetime import datetime

from challenges.models import Submission
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.http import Http404, HttpResponseRedirect
from timeslot.models import TimeSlot
from timeslot.utils import unshorten_object
from tower import ugettext as _


def get_lock_key(object_id):
    """Determines the key to use for locking the ``TimeSlot``"""
    return 'locked-%s' % object_id


def lock_booking(func):
    """Locks the current view for a given period of time,
    until the user hits another locked URL"""
    def _decorated(request, *args, **kwargs):
        entry = kwargs['entry']
        key = get_lock_key(kwargs['object_id'])
        entry_id = cache.get(key)
        # lock the entry and set the expire date
        if not entry_id:
            cache.set(key, entry.id, settings.BOOKING_EXPIRATION)
        # it is free or already has been locked for this entry
        if not entry_id or entry_id == entry.id:
            return func(request, *args, **kwargs)
        # someone has locked in this view
        message = _('Unfortunately his slot has become unavailable')
        messages.error(request, message)
        return HttpResponseRedirect(reverse('timeslot:object_list'),
                                    args=[entry.id])
    return _decorated


def entry_available_decorator(func):
    """Makes sure the ``entry`` is available to be Booked
    - User owns the submission
    - Submission is a winner
    """
    def _decorated(*args, **kwargs):
        request = args[0]
        entry_id = kwargs.pop('entry_id')
        # user owns the submission and it's a winner
        try:
            entry = Submission.objects.get(id=entry_id, is_winner=True,
                                           created_by__user=request.user)
        except Submission.DoesNotExist:
            raise Http404
        # booking has been done
        if TimeSlot.objects.filter(submission=entry, is_booked=True):
            message = _('You have already booked a timeslot for this entry')
            messages.success(request, message)
            return HttpResponseRedirect(entry.get_absolute_url())
        kwargs['entry'] = entry
        return func(*args, **kwargs)
    return _decorated


@login_required
@entry_available_decorator
def object_list(request, entry, template='timeslot/object_list.html'):
    """Listing of the timeslots available for a given entry"""
    object_list = TimeSlot.objects.all()
    context = {
        'object_list': object_list,
        'entry': entry,
        }
    return jingo.render(request, template, context)


@login_required
@require_POST
@entry_available_decorator
@lock_booking
def object_detail(request, entry, object_id):
    """Books a ``TimeSlot`` for the ``Entry``"""
    timeslot = unshorten_object(object_id)
    if not timeslot:
        raise Http404
    # asign the ``TimeSlot`` to the ``Submission``
    timeslot.submission = entry
    timeslot.booking_date = datetime.utcnow()
    timeslot.is_booked = True
    timeslot.save()
    message = _('Your booking has been successful')
    messages.success(request, message)
    context = {'entry': entry,
               'timeslot': timeslot}
    # Temporaly send the email through the instance
    # this will be moved to a queue
    if request.user.email:
        email_template = lambda x: 'timeslot/email/confirmation_%s.txt'
        subject = jingo.render_to_string(request, email_template('subject'),
                                         context)
        # remove empty lines
        subject = subject.splitlines()[0]
        body = jingo.render_to_string(request, email_template('body'),
                                      context)
        profile = request.user.get_profile()
        recipient = '%s <%s>' % (profile.name, request.user.email)
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
                  [recipient, ], fail_silently=False)
    return HttpResponseRedirect(entry.get_absolute_url())

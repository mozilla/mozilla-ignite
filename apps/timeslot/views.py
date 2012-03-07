import jingo

from datetime import datetime, timedelta

from challenges.models import Submission
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.http import Http404, HttpResponseRedirect
from commons.helpers import get_page
from timeslot.models import TimeSlot
from timeslot.utils import unshorten_object
from tower import ugettext as _

if 'django_mailer' in settings.INSTALLED_APPS:
    from django_mailer import send_mail
else:
    from django.core.mail import send_mail


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
        return HttpResponseRedirect(reverse('timeslot:object_list',
                                            args=[entry.id]))
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
    # Book timeslots start at least 24 hours in advance
    start_date = datetime.utcnow() + timedelta(hours=24)
    timeslot_qs = TimeSlot.objects.filter(start_date__gte=start_date,
                                          is_booked=False)
    paginator = Paginator(timeslot_qs, settings.PAGINATOR_SIZE)
    page_number = get_page(request.GET)
    try:
        page = paginator.page(page_number)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)
    context = {
        'page': page,
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
    # make sure it hasn't been booked
    if timeslot.is_booked:
        # someone has locked in this timeslot
        message = _('Unfortunately his slot has become unavailable')
        messages.error(request, message)
        return HttpResponseRedirect(reverse('timeslot:object_list',
                                            args=[entry.id]))
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
    if request.user.email and settings.BOOKING_SEND_EMAILS:
        email_template = lambda x: 'timeslot/email/confirmation_%s.txt' % x
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


@login_required
def pending(request, template='timeslot/pending.html'):
    """Lists the Pending ideas to be booked for this User"""
    profile = request.user.get_profile()
    now = datetime.utcnow()
    # already booked timeslots for this user
    booked_qs = (TimeSlot.objects.select_related('submission').
                 filter(submission__created_by=profile, is_booked=True))
    booked_ids = [i.submission.id for i in booked_qs]
    # missing timeslots for this user
    submission_list = (Submission.objects.green_lit().
                       select_related('created_by').
                       filter(~Q(id__in=booked_ids), created_by=profile))
    context = {
        'object_list': submission_list,
        'profile': profile,
        }
    return jingo.render(request, template, context)

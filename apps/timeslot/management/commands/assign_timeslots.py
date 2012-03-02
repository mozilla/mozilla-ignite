from datetime import timedelta, datetime

from django.db.models import Q
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from challenges.models import Submission, Phase
from timeslot.models import BookingAvailability

class Command(BaseCommand):
    help = """Throttles the booking of the winning submissions,
    and email the users when they are going to be ready"""

    def handle(self, *args, **options):
        # submitions allocated
        booked_qs = BookingAvailability.objects.all()
        submitions_ids = [item.submission.id for item in booked_qs]
        phase = Phase.objects.get_ideation_phase()
        # make sure the ideation phase has finished
        if phase.end_date > datetime.utcnow():
            raise CommandError('This command can only be run after '
                               'the Ideation phase has finished. '
                               'Try again after: %s' % phase.end_date)
        # winner entries for ideation phase that haven't been allocated
        object_list = Submission.objects.green_lit().\
            filter(~Q(id__in=submitions_ids), phase=phase).order_by('?')
        print 'Allocating %s entries' % len(object_list)
        # allocation starts right after this command has been run
        allocation_date = datetime.utcnow()
        date_increments = timedelta(seconds=settings.BOOKING_THROTTLING_TIMEDELTA)
        print 'Allocationg timeslots from: %s' % allocation_date
        for i, submission in enumerate(object_list):
            # Increase availability date for this batch when the
            # limit has been reached and if throttling is enabled
            if i and not i % settings.BOOKING_THROTTLING_USERS and \
                settings.BOOKING_THROTTLING:
                allocation_date += date_increments
            data = {
                'submission': submission,
                'available_on': allocation_date,
                }
            booking = BookingAvailability.objects.create(**data)
            print ' %s created' % booking

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Context
from challenges.models import Submission
from timeslot.models import Release
from timeslot.notifications import send_reminder

if 'django_mailer' in settings.INSTALLED_APPS:
    from django_mailer import send_mail
else:
    from django.core.mail import send_mail



class Command(BaseCommand):
    help = """Notifies the green lit teams when they are ready to book"""

    def handle(self, *args, **options):
        release = Release.objects.get_current()
        if not release:
            raise CommandError('There is not an active Release')
        answer = raw_input("This will remind INMEDIATELY the green-lit teams "
                           "that haven't book a timeslot for the '%s' release."
                           " Proceed? (yes/no)? " % release)
        if answer != 'yes':
            raise CommandError('Phew. Submission canceled.')
        submission_list = (Submission.objects
                           .non_booked_submissions(release))
        sent_emails = send_reminder(submission_list, {'release': release})
        print 'Emailed %s recipients' % sent_emails

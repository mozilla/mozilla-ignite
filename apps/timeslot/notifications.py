from django.template import Context
from django.template.loader import render_to_string
from django.conf import settings

if 'django_mailer' in settings.INSTALLED_APPS:
    from django_mailer import send_mail
else:
    from django.core.mail import send_mail


def send_reminder(submission_list, extra_context=None):
    """Emails the ``Submissions`` a reminder of the timeslot"""
    email_template = lambda x: 'timeslot/email/reminder/%s.txt' % x
    sent_emails = 0
    for submission in submission_list:
        profile = submission.created_by
        if not profile.user.email:
            continue
        context = {
            'submission': submission,
            'profile': profile,
            'site_url': settings.SITE_URL,
            }
        if extra_context:
            context.update(extra_context)
        context = Context(context)
        subject = render_to_string(email_template('subject'), context)
        subject = subject.splitlines()[0]
        body = render_to_string(email_template('body'), context)
        recipient = '%s <%s>' % (profile.name, profile.user.email)
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient],
                  fail_silently=False)
        sent_emails += 1
    return sent_emails


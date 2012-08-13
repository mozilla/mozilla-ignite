from django.contrib import admin
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns, url
from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponseRedirect

from timeslot.models import TimeSlot, Release
from challenges.models import Submission
from timeslot.notifications import send_reminder


class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['start_date', 'end_date', 'is_booked', 'submission',
                    'release']
    list_filter = ['release__name', 'is_booked']


class ReleaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_current', 'phase', 'phase_round']
    change_list_template = 'admin/timeslot/reminders_change_list.html'
    def get_urls(self):
        urls = super(ReleaseAdmin, self).get_urls()
        custom_urls = patterns(
            '',
            url(r'^reminders/$',
                self.admin_site.admin_view(self.send_reminder),
                name='send_reminder'
                )
            )
        return custom_urls + urls

    def send_reminder(self, request):
        release = Release.objects.get_current()
        if release:
            submission_list = (Submission.objects
                               .non_booked_submissions(release))
        else:
            submission_list = []
        if release and request.method == 'POST':
            sent_emails = send_reminder(submission_list,
                                        {'release': release})
            self.message_user(request, "Successfully sent %s reminders" %
                              sent_emails)
            success_url = reverse('admin:timeslot_release_changelist')
            return HttpResponseRedirect(success_url)
        context = {
            'release': release,
            'submission_list': submission_list
            }
        return render(request, 'admin/timeslot/reminders.html', context)

admin.site.register(TimeSlot, TimeSlotAdmin)
admin.site.register(Release, ReleaseAdmin)

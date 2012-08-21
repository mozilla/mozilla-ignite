from awards.models import JudgeAllowance, SubmissionAward, Award
from awards.forms import AwardAdminForm
from challenges.judging import get_judge_profiles
from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect


class JudgeAllowanceInline(admin.TabularInline):
    model = JudgeAllowance
    extra = 0


class AwardAdmin(admin.ModelAdmin):
    inlines = [JudgeAllowanceInline]
    form = AwardAdminForm
    list_display = ['amount', 'phase', 'phase_round']

    def get_urls(self):
        urls = super(AwardAdmin, self).get_urls()
        custom_urls = patterns(
            '',
            url(r'^(?P<award_id>\d+)/distribute/$',
                self.admin_site.admin_view(self.distribute),
                name='awards_distribute')
            )
        return custom_urls + urls

    def distribute(self, request, award_id):
        """Distribute the money evenly between all the Judges"""
        try:
            award = Award.objects.get(id=award_id)
        except Award.DoesNotExist:
            raise Http404
        change_url = reverse('admin:awards_award_change', args=[award.id])
        if award.judgeallowance_set.all():
            self.message_user(request, 'This amount has already been distributed')
            return HttpResponseRedirect(change_url)
        judge_list = get_judge_profiles()
        if not judge_list:
            self.message_user(request, 'There are no Judges to assing the Award')
            return HttpResponseRedirect(change_url)
        amount = award.amount / len(judge_list)
        for judge in judge_list:
            JudgeAllowance.objects.create(amount=amount,
                                          judge=judge,
                                          award=award)
        self.message_user(request, 'Amount distributed between %s Judges'
                          '' % len(judge_list))
        return HttpResponseRedirect(change_url)


class SubmissionAwardInline(admin.TabularInline):
    model = SubmissionAward


class JudgeAllowanceAdmin(admin.ModelAdmin):
    inlines = [SubmissionAwardInline]


admin.site.register(JudgeAllowance, JudgeAllowanceAdmin)
admin.site.register(Award, AwardAdmin)

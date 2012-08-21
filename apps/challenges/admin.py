from datetime import datetime

from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.options import IncorrectLookupParameters
from django.core.paginator import InvalidPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.admin.views.main import ChangeList



from challenges.forms import PhaseRoundAdminForm, JudgingAssignmentAdminForm
from challenges.judging import (get_judge_profiles, get_submissions,
                                get_assignments)
from challenges.models import (Challenge, Phase, Submission, ExternalLink,
                               Category, ExclusionFlag, JudgingCriterion,
                               JudgingAnswer, Judgement, JudgeAssignment,
                               PhaseCriterion, PhaseRound, SubmissionParent,
                               SubmissionVersion, SubmissionHelp)
from badges.models import SubmissionBadge


class JudgeAwareUserAdmin(UserAdmin):
    
    def is_judge(self, user):
        judge_permission = Permission.objects.get(codename='judge_submission')
        judges = User.objects.filter(Q(user_permissions=judge_permission) |
                                     Q(groups__permissions=judge_permission))
        return user in judges
    
    # Enable the pretty tick boxes in the Django admin
    is_judge.boolean = True
    
    list_display = UserAdmin.list_display + ('is_judge',)


class PhaseInline(admin.TabularInline):
    
    model = Phase
    

class PhaseCriterionInline(admin.TabularInline):
    
    model = PhaseCriterion

class CategoryAdmin(admin.ModelAdmin):
    
    model = Category
    prepopulated_fields = {"slug": ("name",)}


class JudgeAssignmentInline(admin.StackedInline):
    
    model = JudgeAssignment
    max_num = 1


class ExclusionFlagInline(admin.StackedInline):
    model = ExclusionFlag
    extra = 1


class PhaseRoundInline(admin.TabularInline):
    model = PhaseRound
    form = PhaseRoundAdminForm
    extra = 1

class PhaseAdmin(admin.ModelAdmin):
    change_list_template = 'admin/phases/phases_change_list.html'
    inlines = (PhaseCriterionInline, PhaseRoundInline)

    def get_urls(self):
        urls = super(PhaseAdmin, self).get_urls()
        custom_urls = patterns(
            '',
            url(r'^assign-judges/$',
                self.admin_site.admin_view(self.assign_judges),
                name='assign_judges')
            )
        return custom_urls + urls

    def assign_judges(self, request):
        """Assign judges for the selected finished ``Phase`` or ``PhaseRound``"""
        now = datetime.utcnow()
        judge_profiles = get_judge_profiles()
        if request.method == 'POST':
            form = JudgingAssignmentAdminForm(request.POST,
                                              judge_profiles=judge_profiles)
            if form.is_valid():
                cleaned_data = form.cleaned_data
                submissions = get_submissions(cleaned_data['phase'],
                                              cleaned_data['phase_round'])
                judges_submission = cleaned_data['judges_per_submission']
                assignments = get_assignments(submissions, judge_profiles,
                                              commit=True,
                                              judges_per_submission=judges_submission)
                self.message_user(request, "Successfully assigned %s submissions "
                                  "to %s judges with %s judges per submission" %
                                  (len(submissions), len(judge_profiles),
                                   judges_submission))
                return HttpResponseRedirect(reverse('admin:challenges_phase_changelist'))
        else:
            form = JudgingAssignmentAdminForm(judge_profiles=judge_profiles)
        context = {
            'now': now,
            'judge_profiles': judge_profiles,
            'form': form,
            }
        return render(request, 'admin/phases/assign_judges.html', context)


class SubmissionBadgeInline(admin.TabularInline):
    model = SubmissionBadge



MAX_SHOW_ALL_ALLOWED = 200

class SubmissionChangeList(ChangeList):
    """Overide specific methods related to the ordering of the queryset.

    We override these methods because we need to order by ``score``
    which is a property that can't be agregated (is calculated with the
    output from other tables).
    """

    def __init__(self, *args, **kwargs):
        self.request = args[0]
        super(SubmissionChangeList, self).__init__(*args, **kwargs)

    def get_query_set(self):
        """Performs the sorting and transform the ``query_set`` into a list
        This is the last step of all the filtering and sorting.
        Beware of any aggregation happening in the template, if so it will
        break when a list is passed.
        """
        qs = super(SubmissionChangeList, self).get_query_set()
        # the dummy ``score`` ordering is in the colum 8
        # used only AFTER all the filters have been applied
        # IMPORTANT: if the order of the columns change this should be amended
        # and we only alter the ordering when the request is ``GET``
        if self.params.get('o') == '8' and not self.request.method == 'POST':
            return sorted(qs, key=lambda s: s.score,
                          reverse=(self.params.get('ot') == 'desc'))
        return qs

    def get_results(self, request):
        """This is a duplicate of the admin method. Replaces
        variables set where it would require a queryset such as the
        number of results"""
        paginator = self.model_admin.get_paginator(request, self.query_set,
                                                   self.list_per_page)
        # Get the number of objects, with admin filters applied.
        result_count = paginator.count
        # Get the total number of objects, with no admin filters applied.
        # Perform a slight optimization: Check to see whether any filters were
        # given. If not, use paginator.hits to calculate the number of objects,
        # because we've already done paginator.hits and the value is cached.
        full_result_count = len(self.query_set)
        can_show_all = result_count <= MAX_SHOW_ALL_ALLOWED
        multi_page = result_count > self.list_per_page

        # Get the list of objects to display on this page.
        if (self.show_all and can_show_all) or not multi_page:
            result_list = self.query_set
        else:
            try:
                result_list = paginator.page(self.page_num+1).object_list
            except InvalidPage:
                raise IncorrectLookupParameters

        self.result_count = result_count
        self.full_result_count = full_result_count
        self.result_list = result_list
        self.can_show_all = can_show_all
        self.multi_page = multi_page
        self.paginator = paginator
        self.request = request


def mark_as_winner(modeladmin, request, queryset):
    """Mark the queryset given as winner."""
    queryset.update(is_winner=True)
mark_as_winner.description = "Mark Submissions as winners"

class SubmissionAdmin(admin.ModelAdmin):
    model = Submission
    list_display = ('title', 'created_by', 'category', 'phase',
                    'is_draft', 'is_winner', 'excluded', 'score',
                    'judge_assignment', 'judgement_count')
    list_filter = ('category', 'is_draft', 'is_winner', 'phase__name',
                   'phase_round__name', 'created_on')
    search_fields = ('title', 'created_by__user__email', 'brief_description',
                     'description')
    list_select_related = True  # For the judgement fields
    inlines = (JudgeAssignmentInline, ExclusionFlagInline,
               SubmissionBadgeInline)
    actions = [mark_as_winner]

    def judge_assignment(self, submission):
        """Return the names of all judges assigned to this submission."""
        assignments = submission.judgeassignment_set.all()
        if not assignments:
            return 'No judge'
        else:
            return ', '.join(a.judge.display_name for a in assignments)

    def excluded(self, submission):
        return submission.exclusionflag_set.exists()
    excluded.boolean = True

    def judgement_count(self, submission):
        return submission.judgement_set.count()

    def get_changelist(self, request, **kwargs):
        """Returns our custom ChangeList class for use on the
        changelist page."""
        return SubmissionChangeList

    def score(self, submission):
        """Define a custom attribute to show and sort in the ModelAdmin
        Uses a dummy attribute so it can sort without complaining"""
        return submission.score
    score.admin_order_field = 'id'

class ChallengeAdmin(admin.ModelAdmin):
    
    prepopulated_fields = {"slug": ("title",)}
    inlines = (PhaseInline,)


class JudgingCriterionAdmin(admin.ModelAdmin):
    
    list_display = ('question', 'max_value')


class JudgingAnswerInline(admin.StackedInline):
    
    model = JudgingAnswer


class JudgementAdmin(admin.ModelAdmin):
    
    inlines = (JudgingAnswerInline,)
    list_display = ('__unicode__', 'submission', 'judge', 'complete', 'score')
    
    def complete(self, judgement):
        try:
            judgement.get_score()
        except Judgement.Incomplete:
            return False
        else:
            return True
    
    complete.boolean = True
    
    def score(self, judgement):
        try:
            return judgement.get_score()
        except Judgement.Incomplete:
            return 'Incomplete'


class ExclusionFlagAdmin(admin.ModelAdmin):
    model = ExclusionFlag
    list_display = ('submission', 'notes')


class PhaseRoundAdmin(admin.ModelAdmin):
    model = PhaseRound
    form = PhaseRoundAdminForm
    list_display = ['name', 'start_date', 'end_date', 'phase']
    list_filter = ['phase__name']


class SubmissionVersionInline(admin.TabularInline):
    model = SubmissionVersion


class SubmissionParentAdmin(admin.ModelAdmin):
    inlines = [SubmissionVersionInline]
    list_display = ['name', 'submission', 'slug', 'is_featured']
    list_filter = ['is_featured', 'status']
    search_fields = ['name', 'submission__title', 'slug']


admin.site.unregister(User)
admin.site.register(User, JudgeAwareUserAdmin)

admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(ExternalLink)
admin.site.register(Phase, PhaseAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ExclusionFlag, ExclusionFlagAdmin)

admin.site.register(JudgingCriterion, JudgingCriterionAdmin)
admin.site.register(Judgement, JudgementAdmin)
admin.site.register(JudgeAssignment)
admin.site.register(SubmissionParent, SubmissionParentAdmin)
admin.site.register(SubmissionHelp)

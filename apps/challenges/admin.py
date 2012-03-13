from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q

from challenges.forms import PhaseRoundAdminForm
from challenges.models import (Challenge, Phase, Submission, ExternalLink,
                               Category, ExclusionFlag, JudgingCriterion,
                               JudgingAnswer, Judgement, JudgeAssignment,
                               PhaseCriterion, PhaseRound)
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


class PhaseAdmin(admin.ModelAdmin):
    
    inlines = (PhaseCriterionInline,)


class SubmissionBadgeInline(admin.TabularInline):
    model = SubmissionBadge


class SubmissionAdmin(admin.ModelAdmin):
    model = Submission
    list_display = ('title', 'created_by', 'category', 'phase', 'is_draft',
                    'is_winner', 'excluded', 'judge_assignment',
                    'judgement_count')
    list_filter = ('category', 'is_draft', 'is_winner')
    list_select_related = True  # For the judgement fields
    inlines = (JudgeAssignmentInline, ExclusionFlagInline,
               SubmissionBadgeInline)

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
admin.site.register(PhaseRound, PhaseRoundAdmin)

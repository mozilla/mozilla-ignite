from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q

from challenges.models import Challenge, Phase, Submission, ExternalLink, Category
from challenges.models import JudgingCriterion, JudgingAnswer, Judgement, JudgeAssignment


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

class CategoryAdmin(admin.ModelAdmin):
    
    model = Category
    prepopulated_fields = {"slug": ("name",)}


class JudgeAssignmentInline(admin.StackedInline):
    
    model = JudgeAssignment
    max_num = 1


class SubmissionAdmin(admin.ModelAdmin):
    
    model = Submission
    list_display = ('title', 'created_by', 'category', 'phase', 'is_live',
                    'is_winner', 'judge_assignment', 'judgement_count')
    list_filter = ('category', 'is_live', 'is_winner')
    list_select_related = True  # For the judgement fields
    
    inlines = (JudgeAssignmentInline,)
    
    def judge_assignment(self, submission):
        """Return the names of all judges assigned to this submission."""
        assignments = submission.judgeassignment_set.all()
        if not assignments:
            return 'No judge'
        else:
            return ', '.join(a.judge.display_name for a in assignments)
    
    def judgement_count(self, submission):
        return submission.judgement_set.count()


class ChallengeAdmin(admin.ModelAdmin):
    
    prepopulated_fields = {"slug": ("title",)}
    inlines = (PhaseInline,)


class JudgingCriterionAdmin(admin.ModelAdmin):
    
    list_display = ('question', 'min_value', 'max_value')


class JudgingAnswerInline(admin.StackedInline):
    
    model = JudgingAnswer


class JudgementAdmin(admin.ModelAdmin):
    
    inlines = (JudgingAnswerInline,)
    list_display = ('__unicode__', 'submission', 'judge')

admin.site.unregister(User)
admin.site.register(User, JudgeAwareUserAdmin)

admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(ExternalLink)
admin.site.register(Phase)
admin.site.register(Category, CategoryAdmin)

admin.site.register(JudgingCriterion, JudgingCriterionAdmin)
admin.site.register(Judgement, JudgementAdmin)
admin.site.register(JudgeAssignment)

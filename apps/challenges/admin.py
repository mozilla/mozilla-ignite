from django.contrib import admin

from challenges.models import Challenge, Phase, Submission, ExternalLink, Category
from challenges.models import JudgingCriterion, JudgingAnswer, Judgement


class PhaseInline(admin.TabularInline):
    
    model = Phase

class CategoryAdmin(admin.ModelAdmin):
    
    prepopulated_fields = {"slug": ("name",)}


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


admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Submission)
admin.site.register(ExternalLink)
admin.site.register(Phase)
admin.site.register(Category, CategoryAdmin)

admin.site.register(JudgingCriterion, JudgingCriterionAdmin)
admin.site.register(Judgement, JudgementAdmin)

from awards.models import JudgeAllowance, SubmissionAward
from django.contrib import admin


class SubmissionAwardInline(admin.TabularInline):
    model = SubmissionAward


class JudgeAllowanceAdmin(admin.ModelAdmin):
    inlines = [SubmissionAwardInline]


admin.site.register(JudgeAllowance, JudgeAllowanceAdmin)

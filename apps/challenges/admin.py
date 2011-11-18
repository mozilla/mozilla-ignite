from django.contrib import admin

from challenges.models import Challenge, Phase, Submission, ExternalLink


class PhaseInline(admin.TabularInline):
    
    model = Phase


class ChallengeAdmin(admin.ModelAdmin):
    
    prepopulated_fields = {"slug": ("title",)}
    inlines = (PhaseInline,)


admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Submission)
admin.site.register(ExternalLink)

from django.contrib import admin

from challenges.models import Challenge, Phase, Submission, ExternalLink, Category


class PhaseInline(admin.TabularInline):
    
    model = Phase

class CategoryAdmin(admin.ModelAdmin):
    
    prepopulated_fields = {"slug": ("name",)}


class ChallengeAdmin(admin.ModelAdmin):
    
    prepopulated_fields = {"slug": ("title",)}
    inlines = (PhaseInline,)


admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Submission)
admin.site.register(ExternalLink)
admin.site.register(Phase)
admin.site.register(Category, CategoryAdmin)

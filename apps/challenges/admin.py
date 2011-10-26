from django.contrib import admin

from challenges.models import Challenge, Submission

class ChallengeAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Submission)

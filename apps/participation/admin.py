from django.contrib import admin

from participation.models import Participation, Entry

class ParticipationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Participation, ParticipationAdmin)
admin.site.register(Entry)

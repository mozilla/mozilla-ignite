from django.contrib import admin
from timeslot.models import TimeSlot, Release


class TimeSlotAdmin(admin.ModelAdmin):
    pass

class ReleaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_current']

admin.site.register(TimeSlot, TimeSlotAdmin)
admin.site.register(Release, ReleaseAdmin)

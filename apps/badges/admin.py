from django.contrib import admin
from badges.models import Badge


class BadgeAdmin(admin.ModelAdmin):
    list_display = ('badge_type', 'body')
    list_filter = ('badge_type',)


admin.site.register(Badge, BadgeAdmin)

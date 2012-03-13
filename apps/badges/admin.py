from django.contrib import admin
from badges.models import Badge, SubmissionBadge


def acknowledge_action(items, modeladmin, request, extra_text=""):
    """Sends a message acknowledging the action"""
    if items == 1:
        text = "1 %s" % modeladmin.model._meta.verbose_name
    else:
        text = "%s %s were" % (items,
                               unicode(modeladmin.model._meta.verbose_name_plural))
    acknowledge_text = "%s successfully %s" % (text, extra_text)
    modeladmin.message_user(request, acknowledge_text)


def publish_objects(modeladmin, request, queryset):
    """Publishes the selected ``Badges``"""
    qs = {'is_published': True}
    items = queryset.update(**qs)
    acknowledge_action(items, modeladmin, request, "published")
publish_objects.short_description = "Publish Badges on Submission page"


class BadgeAdmin(admin.ModelAdmin):
    list_display = ('badge_type', 'body')
    list_filter = ('badge_type',)


class SubmissionBadgeAdmin(admin.ModelAdmin):
    list_display = ('badge', 'submission', 'is_published')
    list_filter = ('badge__badge_type', 'is_published')
    actions = [publish_objects]


admin.site.register(Badge, BadgeAdmin)
admin.site.register(SubmissionBadge, SubmissionBadgeAdmin)

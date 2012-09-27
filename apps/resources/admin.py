from django.contrib import admin
from resources.models import Resource


class ResourceAdmin(admin.ModelAdmin):
    model = Resource
    list_display = ('title', 'status', 'resource_type')
    list_filter = ('status', 'resource_type')

admin.site.register(Resource, ResourceAdmin)

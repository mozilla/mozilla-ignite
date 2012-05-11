from django.contrib import admin

from events.models import Event, Venue


class EventAdmin(admin.ModelAdmin):
    fields = ('name', 'slug', 'start', 'end', 'description', 'url',
              'venue', 'featured', 'created_by')
    prepopulated_fields = {'slug': ('name',)}


class VenueAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', 'city')}


admin.site.register(Event, EventAdmin)
admin.site.register(Venue, VenueAdmin)

from django.contrib import admin
from timeslot.models import TimeSlot, BookingAvailability

admin.site.register([TimeSlot, BookingAvailability])

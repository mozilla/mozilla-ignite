from django.contrib import admin
from timeslot.models import TimeSlot, Booking

admin.site.register([TimeSlot, Booking, ])

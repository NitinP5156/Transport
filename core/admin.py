from django.contrib import admin
from .models import User, StudentProfile, DriverProfile, Bus, Route, Booking, LeaveRequest, ServiceLog

admin.site.register(User)
admin.site.register(StudentProfile)
admin.site.register(DriverProfile)
admin.site.register(Bus)
admin.site.register(Route)
admin.site.register(Booking)
admin.site.register(LeaveRequest)
admin.site.register(ServiceLog) 
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_driver = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    @property
    def is_site_admin(self):
        return self.is_superuser or self.is_admin

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add more student-specific fields if needed

class DriverProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    leave_balance = models.IntegerField(default=0)
    # Add more driver-specific fields if needed

class Bus(models.Model):
    number = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default='active')
    assigned_driver = models.ForeignKey(DriverProfile, null=True, blank=True, on_delete=models.SET_NULL)

class Route(models.Model):
    start_point = models.CharField(max_length=100)
    end_point = models.CharField(max_length=100)
    stops = models.TextField(help_text='Comma-separated list of stops')
    timings = models.CharField(max_length=100)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)

class Booking(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    seat_number = models.PositiveIntegerField()
    date = models.DateField()
    status = models.CharField(max_length=20, default='booked')

class LeaveRequest(models.Model):
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, default='pending')
    reason = models.TextField()

class ServiceLog(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.TextField()
    status = models.CharField(max_length=20)
    cost = models.DecimalField(max_digits=10, decimal_places=2) 
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout as auth_logout
from .models import User, Route, Booking, StudentProfile, Bus
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import DriverProfile, LeaveRequest, ServiceLog
from django import forms
from django.contrib.auth.forms import AuthenticationForm
import random

# --- Admin Forms ---
class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = ['number', 'capacity', 'status', 'assigned_driver']

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['start_point', 'end_point', 'stops', 'timings', 'bus']

# --- Service Log Form ---
class ServiceLogForm(forms.ModelForm):
    class Meta:
        model = ServiceLog
        fields = ['bus', 'date', 'description', 'status', 'cost']

def home(request):
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    user = request.user
    if user.is_admin:
        return redirect('admin_dashboard')
    elif user.is_driver:
        return redirect('driver_dashboard')
    elif user.is_student:
        return redirect('student_dashboard')
    else:
        auth_logout(request)
        return redirect('home')

def custom_logout(request):
    auth_logout(request)
    return redirect('home')

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')
        if not username or not password or not password2 or not role:
            messages.error(request, 'All fields are required.')
        elif password != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(username=username, password=password)
            if role == 'student':
                user.is_student = True
                user.save()
                StudentProfile.objects.create(user=user)
            elif role == 'driver':
                user.is_driver = True
                user.save()
                DriverProfile.objects.create(user=user)
            login(request, user)
            return redirect('dashboard')
    return render(request, 'core/register.html')

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html', {'form': form})

def custom_admin_login(request):
    if request.user.is_authenticated and request.user.is_site_admin:
        return redirect('/panel/')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            if user.is_site_admin:
                login(request, user)
                return redirect('/panel/')
            else:
                messages.error(request, 'You do not have admin access.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'admin/login.html', {'form': form})

@login_required
def student_dashboard(request):
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    total_bookings = Booking.objects.filter(student=student_profile).count()
    upcoming_bookings = Booking.objects.filter(student=student_profile, date__gte=timezone.now().date()).count()
    available_routes = Route.objects.count()
    next_ride = Booking.objects.filter(student=student_profile, date__gte=timezone.now().date()).order_by('date').first()
    last_booking = Booking.objects.filter(student=student_profile).order_by('-date').first()
    last_route = last_booking.route if last_booking else None
    tips = [
        "Arrive at your stop 5 minutes early!",
        "Always carry your college ID for verification.",
        "Check your booking before you leave home.",
        "Respect your driver and fellow students.",
        "Keep the bus clean and safe for everyone!",
        "Book your seat in advance for busy days.",
    ]
    tip = random.choice(tips)
    return render(request, 'core/student_dashboard.html', {
        'total_bookings': total_bookings,
        'upcoming_bookings': upcoming_bookings,
        'available_routes': available_routes,
        'next_ride': next_ride,
        'last_route': last_route,
        'tip': tip,
    })

@login_required
def driver_dashboard(request):
    return render(request, 'core/driver_dashboard.html')

@login_required
def admin_dashboard(request):
    bus_count = Bus.objects.count()
    route_count = Route.objects.count()
    driver_count = DriverProfile.objects.count()
    pending_leaves = LeaveRequest.objects.filter(status='pending').count()
    return render(request, 'core/admin_dashboard.html', {
        'bus_count': bus_count,
        'route_count': route_count,
        'driver_count': driver_count,
        'pending_leaves': pending_leaves,
    })

@login_required
def list_routes(request):
    routes = Route.objects.select_related('bus').all()
    return render(request, 'core/list_routes.html', {'routes': routes})

@login_required
def book_seat(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    bus = route.bus
    booked_seats = Booking.objects.filter(route=route, date=timezone.now().date()).count()
    available_seats = bus.capacity - booked_seats
    if request.method == 'POST':
        if available_seats > 0:
            seat_number = booked_seats + 1
            Booking.objects.create(
                student=student_profile,
                bus=bus,
                route=route,
                seat_number=seat_number,
                date=timezone.now().date(),
                status='booked'
            )
            messages.success(request, f'Seat {seat_number} booked successfully!')
            return HttpResponseRedirect(reverse('booking_history'))
        else:
            messages.error(request, 'No seats available on this bus for today.')
    return render(request, 'core/book_seat.html', {'route': route, 'bus': bus, 'available_seats': available_seats})

@login_required
def booking_history(request):
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    if request.method == 'POST' and 'cancel_booking_id' in request.POST:
        booking_id = request.POST.get('cancel_booking_id')
        booking = get_object_or_404(Booking, id=booking_id, student=student_profile)
        # Assume route.timings is a string like '08:30 AM' or '17:45'
        from datetime import datetime, timedelta
        from django.utils import timezone
        # Combine booking.date and route.timings to get the scheduled datetime
        try:
            time_str = booking.route.timings.strip().split('-')[0].strip()  # Take first time if range
            # Try parsing with and without AM/PM
            try:
                ride_time = datetime.strptime(time_str, '%I:%M %p').time()
            except ValueError:
                ride_time = datetime.strptime(time_str, '%H:%M').time()
            ride_datetime = datetime.combine(booking.date, ride_time)
            ride_datetime = timezone.make_aware(ride_datetime, timezone.get_current_timezone())
        except Exception:
            ride_datetime = datetime.combine(booking.date, datetime.min.time())
            ride_datetime = timezone.make_aware(ride_datetime, timezone.get_current_timezone())
        now = timezone.now()
        if booking.status == 'booked' and ride_datetime - now > timedelta(minutes=10):
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, 'Booking cancelled successfully.')
        else:
            messages.error(request, 'Cannot cancel within 10 minutes of arrival.')
        return redirect('booking_history')
    bookings = Booking.objects.filter(student=student_profile).select_related('route', 'bus').order_by('-date')
    from django.utils import timezone as djtz
    today = djtz.now().date()
    return render(request, 'core/booking_history.html', {'bookings': bookings, 'today': today})

# --- Admin Views ---
@login_required
def manage_buses(request):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    buses = Bus.objects.select_related('assigned_driver').all()
    return render(request, 'core/manage_buses.html', {'buses': buses})

@login_required
def add_bus(request):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    if request.method == 'POST':
        form = BusForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus added successfully!')
            return redirect('manage_buses')
    else:
        form = BusForm()
    return render(request, 'core/add_edit_bus.html', {'form': form, 'edit': False})

@login_required
def edit_bus(request, bus_id):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    bus = get_object_or_404(Bus, id=bus_id)
    if request.method == 'POST':
        form = BusForm(request.POST, instance=bus)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus updated successfully!')
            return redirect('manage_buses')
    else:
        form = BusForm(instance=bus)
    return render(request, 'core/add_edit_bus.html', {'form': form, 'edit': True})

@login_required
def delete_bus(request, bus_id):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    bus = get_object_or_404(Bus, id=bus_id)
    bus.delete()
    messages.success(request, 'Bus deleted successfully!')
    return redirect('manage_buses')

@login_required
def manage_routes(request):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    routes = Route.objects.select_related('bus').all()
    return render(request, 'core/manage_routes.html', {'routes': routes})

@login_required
def add_route(request):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route added successfully!')
            return redirect('manage_routes')
    else:
        form = RouteForm()
    return render(request, 'core/add_edit_route.html', {'form': form, 'edit': False})

@login_required
def edit_route(request, route_id):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    route = get_object_or_404(Route, id=route_id)
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route updated successfully!')
            return redirect('manage_routes')
    else:
        form = RouteForm(instance=route)
    return render(request, 'core/add_edit_route.html', {'form': form, 'edit': True})

@login_required
def delete_route(request, route_id):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    route = get_object_or_404(Route, id=route_id)
    route.delete()
    messages.success(request, 'Route deleted successfully!')
    return redirect('manage_routes')

# --- Admin Leave Management ---
@login_required
def manage_leaves(request):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    leaves = LeaveRequest.objects.select_related('driver__user').all().order_by('-start_date')
    return render(request, 'core/manage_leaves.html', {'leaves': leaves})

@login_required
def approve_leave(request, leave_id):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    leave.status = 'approved'
    leave.save()
    messages.success(request, 'Leave approved.')
    return redirect('manage_leaves')

@login_required
def reject_leave(request, leave_id):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    leave.status = 'rejected'
    leave.save()
    messages.success(request, 'Leave rejected.')
    return redirect('manage_leaves')

# --- Admin Service Log Management ---
@login_required
def manage_service_logs(request):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    logs = ServiceLog.objects.select_related('bus').all().order_by('-date')
    return render(request, 'core/manage_service_logs.html', {'logs': logs})

@login_required
def add_service_log(request):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    if request.method == 'POST':
        form = ServiceLogForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service log added.')
            return redirect('manage_service_logs')
    else:
        form = ServiceLogForm()
    return render(request, 'core/add_edit_service_log.html', {'form': form, 'edit': False})

@login_required
def edit_service_log(request, log_id):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    log = get_object_or_404(ServiceLog, id=log_id)
    if request.method == 'POST':
        form = ServiceLogForm(request.POST, instance=log)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service log updated.')
            return redirect('manage_service_logs')
    else:
        form = ServiceLogForm(instance=log)
    return render(request, 'core/add_edit_service_log.html', {'form': form, 'edit': True})

@login_required
def delete_service_log(request, log_id):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    log = get_object_or_404(ServiceLog, id=log_id)
    log.delete()
    messages.success(request, 'Service log deleted.')
    return redirect('manage_service_logs')

# --- Driver Panel: Apply for Leave, View Assigned Bus/Route ---
@login_required
def apply_leave(request):
    if not request.user.is_driver:
        return redirect('dashboard')
    driver_profile = get_object_or_404(DriverProfile, user=request.user)
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        LeaveRequest.objects.create(
            driver=driver_profile,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='pending'
        )
        messages.success(request, 'Leave request submitted.')
        return redirect('driver_dashboard')
    return render(request, 'core/apply_leave.html')

@login_required
def assigned_bus_route(request):
    if not request.user.is_driver:
        return redirect('dashboard')
    driver_profile = get_object_or_404(DriverProfile, user=request.user)
    bus = Bus.objects.filter(assigned_driver=driver_profile).first()
    route = Route.objects.filter(bus=bus).first() if bus else None
    return render(request, 'core/assigned_bus_route.html', {'bus': bus, 'route': route})

@login_required
def assign_bus(request):
    if not request.user.is_site_admin:
        return redirect('dashboard')
    buses = Bus.objects.select_related('assigned_driver').all()
    drivers = DriverProfile.objects.all()
    if request.method == 'POST':
        bus_id = request.POST.get('bus_id')
        driver_id = request.POST.get('driver_id')
        bus = get_object_or_404(Bus, id=bus_id)
        driver = get_object_or_404(DriverProfile, id=driver_id) if driver_id else None
        bus.assigned_driver = driver
        bus.save()
        messages.success(request, f'Bus {bus.number} assigned to {driver.user.username if driver else "No Driver"}.')
        return redirect('assign_bus')
    return render(request, 'core/assign_bus.html', {'buses': buses, 'drivers': drivers}) 
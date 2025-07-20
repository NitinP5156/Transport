from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('driver/', views.driver_dashboard, name='driver_dashboard'),
    path('panel/', views.admin_dashboard, name='admin_dashboard'),
    path('routes/', views.list_routes, name='list_routes'),
    path('book/<int:route_id>/', views.book_seat, name='book_seat'),
    path('bookings/', views.booking_history, name='booking_history'),
    path('logout/', views.custom_logout, name='logout'),
    path('login/', views.custom_login, name='login'),
    path('register/', views.register, name='register'),
    path('admin/login/', views.custom_admin_login, name='custom_admin_login'),
    # Admin URLs
    path('panel/buses/', views.manage_buses, name='manage_buses'),
    path('panel/buses/add/', views.add_bus, name='add_bus'),
    path('panel/buses/edit/<int:bus_id>/', views.edit_bus, name='edit_bus'),
    path('panel/buses/delete/<int:bus_id>/', views.delete_bus, name='delete_bus'),
    path('panel/routes/', views.manage_routes, name='manage_routes'),
    path('panel/routes/add/', views.add_route, name='add_route'),
    path('panel/routes/edit/<int:route_id>/', views.edit_route, name='edit_route'),
    path('panel/routes/delete/<int:route_id>/', views.delete_route, name='delete_route'),
    path('panel/leaves/', views.manage_leaves, name='manage_leaves'),
    path('panel/service-logs/', views.manage_service_logs, name='manage_service_logs'),
    path('panel/assign-bus/', views.assign_bus, name='assign_bus'),
    # Leave management
    path('panel/leaves/approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('panel/leaves/reject/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    # Service log management
    path('panel/service-logs/add/', views.add_service_log, name='add_service_log'),
    path('panel/service-logs/edit/<int:log_id>/', views.edit_service_log, name='edit_service_log'),
    path('panel/service-logs/delete/<int:log_id>/', views.delete_service_log, name='delete_service_log'),
    # Driver panel
    path('driver/apply-leave/', views.apply_leave, name='apply_leave'),
    path('driver/assigned/', views.assigned_bus_route, name='assigned_bus_route'),
] 
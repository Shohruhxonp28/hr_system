from django.urls import path
from . import views
from . import employee_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),

    # Positions
    path('positions/', views.position_list, name='position_list'),
    path('positions/create/', views.position_create, name='position_create'),
    path('positions/<int:pk>/edit/', views.position_edit, name='position_edit'),
    path('positions/<int:pk>/delete/', views.position_delete, name='position_delete'),

    # Work Schedules
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('schedules/create/', views.schedule_create, name='schedule_create'),
    path('schedules/<int:pk>/edit/', views.schedule_edit, name='schedule_edit'),
    path('schedules/<int:pk>/delete/', views.schedule_delete, name='schedule_delete'),

    # Employees
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),

    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/create/', views.attendance_create, name='attendance_create'),
    path('attendance/bulk/', views.bulk_attendance, name='bulk_attendance'),
    path('attendance/<int:pk>/edit/', views.attendance_edit, name='attendance_edit'),
    path('attendance/<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),

    # Payroll
    path('payroll/', views.payroll_list, name='payroll_list'),
    path('payroll/calculate/', views.payroll_calculate, name='payroll_calculate'),
    path('payroll/<int:pk>/', views.payroll_detail, name='payroll_detail'),
    path('payroll/<int:pk>/paid/', views.payroll_mark_paid, name='payroll_mark_paid'),

    # Reports
    path('reports/', views.reports, name='reports'),

    # Employee Panel
    path('panel/dashboard/', employee_views.employee_dashboard, name='employee_dashboard'),
    path('panel/attendance/', employee_views.employee_attendance, name='employee_attendance'),
    path('panel/calendar/', employee_views.employee_calendar, name='employee_calendar'),
    path('panel/salary/', employee_views.employee_salary, name='employee_salary'),
    path('panel/profile/', employee_views.employee_profile, name='employee_profile'),
    path('panel/face-id/', employee_views.face_id_scan, name='face_id_scan'),
    path('panel/api/face-check/', employee_views.api_face_check, name='api_face_check'),
    path('panel/upload-photo/', employee_views.employee_upload_photo, name='employee_upload_photo'),
    path('panel/api/capture-photo/', employee_views.employee_capture_photo, name='employee_capture_photo'),
]

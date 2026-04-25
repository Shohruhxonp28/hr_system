from django.contrib import admin
from .models import Department, Position, WorkSchedule, WeeklyWorkDays, Employee, Attendance, Payroll


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'base_salary']
    list_filter = ['department']
    search_fields = ['name']


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'late_tolerance_minutes']


@admin.register(WeeklyWorkDays)
class WeeklyWorkDaysAdmin(admin.ModelAdmin):
    list_display = ['schedule', 'day_of_week', 'is_working']
    list_filter = ['schedule', 'is_working']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'last_name', 'first_name', 'department', 'position', 'status', 'salary']
    list_filter = ['department', 'status', 'gender']
    search_fields = ['first_name', 'last_name', 'employee_id', 'phone']
    date_hierarchy = 'hire_date'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in', 'check_out', 'status', 'late_minutes', 'overtime_minutes']
    list_filter = ['status', 'date']
    search_fields = ['employee__first_name', 'employee__last_name']
    date_hierarchy = 'date'


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'base_salary', 'total_deduction', 'net_salary', 'status']
    list_filter = ['status', 'month', 'year']
    search_fields = ['employee__first_name', 'employee__last_name']

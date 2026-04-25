from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import calendar
import json

from .models import Department, Position, WorkSchedule, WeeklyWorkDays, Employee, Attendance, Payroll
from .forms import (DepartmentForm, PositionForm, WorkScheduleForm, EmployeeForm,
                    AttendanceForm, AttendanceFilterForm, PayrollFilterForm)


def staff_required(view_func):
    """Faqat admin/staff foydalanuvchilar kira oladigan sahifalar uchun decorator."""
    return user_passes_test(
        lambda user: user.is_staff or user.is_superuser,
        login_url='employee_dashboard'
    )(view_func)


def get_today_stats():
    today = date.today()
    total_employees = Employee.objects.filter(is_active=True).count()
    today_attendances = Attendance.objects.filter(date=today)
    present = today_attendances.filter(status__in=['present', 'overtime']).count()
    late = today_attendances.filter(status='late').count()
    absent = today_attendances.filter(status='absent').count()
    left = today_attendances.filter(check_out__isnull=False).exclude(status__in=['absent', 'day_off', 'holiday']).count()

    current_month = today.month
    current_year = today.year
    monthly_payroll = Payroll.objects.filter(month=current_month, year=current_year).aggregate(
        total=Sum('net_salary'))['total'] or 0

    return {
        'total_employees': total_employees,
        'today_present': present,
        'today_late': late,
        'today_absent': absent,
        'today_left': left,
        'monthly_payroll': monthly_payroll,
        'today': today,
    }


@login_required
def dashboard(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('employee_dashboard')

    stats = get_today_stats()
    today = date.today()

    # Recent attendance
    recent_attendances = Attendance.objects.filter(date=today).select_related(
        'employee', 'employee__department', 'employee__position')[:15]

    # Department stats
    dept_stats = []
    for dept in Department.objects.all():
        dept_employees = Employee.objects.filter(department=dept, is_active=True).count()
        dept_present = Attendance.objects.filter(
            date=today, employee__department=dept, status__in=['present', 'late', 'overtime', 'incomplete']
        ).count()
        dept_stats.append({
            'name': dept.name,
            'total': dept_employees,
            'present': dept_present,
        })

    # Monthly attendance chart data (last 7 days)
    chart_labels = []
    chart_present = []
    chart_absent = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        chart_labels.append(d.strftime('%d-%b'))
        chart_present.append(Attendance.objects.filter(date=d, status__in=['present', 'late', 'overtime']).count())
        chart_absent.append(Attendance.objects.filter(date=d, status='absent').count())

    context = {
        **stats,
        'recent_attendances': recent_attendances,
        'dept_stats': dept_stats,
        'chart_labels': json.dumps(chart_labels),
        'chart_present': json.dumps(chart_present),
        'chart_absent': json.dumps(chart_absent),
    }
    return render(request, 'core/dashboard.html', context)


# ========== DEPARTMENTS ==========
@login_required
@staff_required
def department_list(request):
    departments = Department.objects.annotate(emp_count=Count('employees', filter=Q(employees__is_active=True)))
    return render(request, 'core/department_list.html', {'departments': departments})


@login_required
@staff_required
def department_create(request):
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Bo'lim muvaffaqiyatli qo'shildi!")
        return redirect('department_list')
    return render(request, 'core/department_form.html', {'form': form, 'title': "Bo'lim qo'shish"})


@login_required
@staff_required
def department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=dept)
    if form.is_valid():
        form.save()
        messages.success(request, "Bo'lim muvaffaqiyatli yangilandi!")
        return redirect('department_list')
    return render(request, 'core/department_form.html', {'form': form, 'title': "Bo'limni tahrirlash", 'obj': dept})


@login_required
@staff_required
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.delete()
        messages.success(request, "Bo'lim o'chirildi!")
        return redirect('department_list')
    return render(request, 'core/confirm_delete.html', {'obj': dept, 'title': "Bo'limni o'chirish"})


# ========== POSITIONS ==========
@login_required
@staff_required
def position_list(request):
    positions = Position.objects.select_related('department').annotate(
        emp_count=Count('employees', filter=Q(employees__is_active=True)))
    return render(request, 'core/position_list.html', {'positions': positions})


@login_required
@staff_required
def position_create(request):
    form = PositionForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Lavozim muvaffaqiyatli qo'shildi!")
        return redirect('position_list')
    return render(request, 'core/position_form.html', {'form': form, 'title': "Lavozim qo'shish"})


@login_required
@staff_required
def position_edit(request, pk):
    pos = get_object_or_404(Position, pk=pk)
    form = PositionForm(request.POST or None, instance=pos)
    if form.is_valid():
        form.save()
        messages.success(request, "Lavozim muvaffaqiyatli yangilandi!")
        return redirect('position_list')
    return render(request, 'core/position_form.html', {'form': form, 'title': "Lavozimni tahrirlash", 'obj': pos})


@login_required
@staff_required
def position_delete(request, pk):
    pos = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        pos.delete()
        messages.success(request, "Lavozim o'chirildi!")
        return redirect('position_list')
    return render(request, 'core/confirm_delete.html', {'obj': pos, 'title': "Lavozimni o'chirish"})


# ========== WORK SCHEDULES ==========
@login_required
@staff_required
def schedule_list(request):
    schedules = WorkSchedule.objects.prefetch_related('work_days')
    return render(request, 'core/schedule_list.html', {'schedules': schedules})


@login_required
@staff_required
def schedule_create(request):
    if request.method == 'POST':
        form_data = request.POST
        schedule = WorkSchedule(
            name=form_data.get('name'),
            start_time=form_data.get('start_time'),
            end_time=form_data.get('end_time'),
            late_tolerance_minutes=int(form_data.get('late_tolerance_minutes', 15)),
            overtime_threshold_minutes=int(form_data.get('overtime_threshold_minutes', 30)),
            description=form_data.get('description', '')
        )
        schedule.save()
        # Save work days
        day_names = {0: 'Dushanba', 1: 'Seshanba', 2: 'Chorshanba', 3: 'Payshanba', 4: 'Juma', 5: 'Shanba', 6: 'Yakshanba'}
        for day_num in range(7):
            is_working = f'day_{day_num}' in form_data
            WeeklyWorkDays.objects.create(schedule=schedule, day_of_week=day_num, is_working=is_working)
        messages.success(request, "Ish jadvali muvaffaqiyatli qo'shildi!")
        return redirect('schedule_list')
    from .forms import WorkScheduleForm
    form = WorkScheduleForm()
    days = [(i, d) for i, d in WeeklyWorkDays.DAYS]
    return render(request, 'core/schedule_form.html', {'form': form, 'title': "Ish jadvali qo'shish", 'days': days})


@login_required
@staff_required
def schedule_edit(request, pk):
    schedule = get_object_or_404(WorkSchedule, pk=pk)
    if request.method == 'POST':
        form_data = request.POST
        schedule.name = form_data.get('name')
        schedule.start_time = form_data.get('start_time')
        schedule.end_time = form_data.get('end_time')
        schedule.late_tolerance_minutes = int(form_data.get('late_tolerance_minutes', 15))
        schedule.overtime_threshold_minutes = int(form_data.get('overtime_threshold_minutes', 30))
        schedule.description = form_data.get('description', '')
        schedule.save()
        for day_num in range(7):
            is_working = f'day_{day_num}' in form_data
            WeeklyWorkDays.objects.update_or_create(
                schedule=schedule, day_of_week=day_num,
                defaults={'is_working': is_working}
            )
        messages.success(request, "Ish jadvali muvaffaqiyatli yangilandi!")
        return redirect('schedule_list')
    from .forms import WorkScheduleForm
    form = WorkScheduleForm(instance=schedule)
    work_days = {wd.day_of_week: wd.is_working for wd in schedule.work_days.all()}
    days = [(i, d, work_days.get(i, False)) for i, d in WeeklyWorkDays.DAYS]
    return render(request, 'core/schedule_form.html', {
        'form': form, 'title': "Ish jadvalini tahrirlash", 'obj': schedule, 'days': days
    })


@login_required
@staff_required
def schedule_delete(request, pk):
    schedule = get_object_or_404(WorkSchedule, pk=pk)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, "Ish jadvali o'chirildi!")
        return redirect('schedule_list')
    return render(request, 'core/confirm_delete.html', {'obj': schedule, 'title': "Ish jadvalini o'chirish"})


# ========== EMPLOYEES ==========
@login_required
@staff_required
def employee_list(request):
    employees = Employee.objects.select_related('department', 'position').filter(is_active=True)
    dept_filter = request.GET.get('department')
    status_filter = request.GET.get('status')
    search = request.GET.get('search', '')
    if dept_filter:
        employees = employees.filter(department_id=dept_filter)
    if status_filter:
        employees = employees.filter(status=status_filter)
    if search:
        employees = employees.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search) |
            Q(employee_id__icontains=search) | Q(phone__icontains=search)
        )
    departments = Department.objects.all()
    return render(request, 'core/employee_list.html', {
        'employees': employees, 'departments': departments,
        'dept_filter': dept_filter, 'status_filter': status_filter, 'search': search
    })


@login_required
@staff_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    recent_attendances = employee.attendances.order_by('-date')[:30]
    recent_payrolls = employee.payrolls.order_by('-year', '-month')[:6]
    today = date.today()
    month_attendances = employee.attendances.filter(date__year=today.year, date__month=today.month)
    month_present = month_attendances.filter(status__in=['present', 'overtime', 'late', 'incomplete']).count()
    month_absent = month_attendances.filter(status='absent').count()
    return render(request, 'core/employee_detail.html', {
        'employee': employee, 'recent_attendances': recent_attendances,
        'recent_payrolls': recent_payrolls, 'month_present': month_present, 'month_absent': month_absent
    })


@login_required
@staff_required
def employee_create(request):
    form = EmployeeForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        employee = form.save(commit=False)

        # Login ma'lumotlari
        username = form.cleaned_data.get('username') or employee.employee_id.lower()
        password = form.cleaned_data.get('password') or (employee.employee_id.lower() + '123')

        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            messages.error(request, f"'{username}' login allaqachon mavjud! Boshqa login kiriting.")
            return render(request, 'core/employee_form.html', {'form': form, 'title': "Xodim qo'shish"})

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=employee.first_name,
            last_name=employee.last_name,
        )
        employee.user = user
        employee.save()

        messages.success(request, f"Xodim qo'shildi! Login: {username} | Parol: {password}")
        return redirect('employee_list')
    return render(request, 'core/employee_form.html', {'form': form, 'title': "Xodim qo'shish"})


@login_required
@staff_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    form = EmployeeForm(request.POST or None, request.FILES or None, instance=employee)

    # Tahrirlashda username maydonini to'ldirish
    if request.method == 'GET' and employee.user:
        form.fields['username'].initial = employee.user.username

    if form.is_valid():
        emp = form.save(commit=False)

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        from django.contrib.auth.models import User

        if emp.user:
            # Mavjud foydalanuvchini yangilash
            if username and username != emp.user.username:
                if User.objects.filter(username=username).exclude(pk=emp.user.pk).exists():
                    messages.error(request, f"'{username}' login allaqachon mavjud!")
                    return render(request, 'core/employee_form.html', {'form': form, 'title': "Xodimni tahrirlash", 'obj': employee})
                emp.user.username = username
            emp.user.first_name = emp.first_name
            emp.user.last_name = emp.last_name
            if password:
                emp.user.set_password(password)
            emp.user.save()
        else:
            # Yangi foydalanuvchi yaratish
            uname = username or emp.employee_id.lower()
            pwd = password or (emp.employee_id.lower() + '123')
            if User.objects.filter(username=uname).exists():
                messages.error(request, f"'{uname}' login allaqachon mavjud!")
                return render(request, 'core/employee_form.html', {'form': form, 'title': "Xodimni tahrirlash", 'obj': employee})
            user = User.objects.create_user(username=uname, password=pwd, first_name=emp.first_name, last_name=emp.last_name)
            emp.user = user
            messages.info(request, f"Yangi login yaratildi: {uname} | Parol: {pwd}")

        emp.save()
        messages.success(request, "Xodim muvaffaqiyatli yangilandi!")
        return redirect('employee_list')
    return render(request, 'core/employee_form.html', {'form': form, 'title': "Xodimni tahrirlash", 'obj': employee})


@login_required
@staff_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.is_active = False
        employee.save()
        messages.success(request, "Xodim o'chirildi!")
        return redirect('employee_list')
    return render(request, 'core/confirm_delete.html', {'obj': employee, 'title': "Xodimni o'chirish"})


# ========== ATTENDANCE ==========
@login_required
@staff_required
def attendance_list(request):
    form = AttendanceFilterForm(request.GET or None)
    attendances = Attendance.objects.select_related('employee', 'employee__department', 'employee__position')

    if form.is_valid():
        data = form.cleaned_data
        if data.get('date_from'):
            attendances = attendances.filter(date__gte=data['date_from'])
        if data.get('date_to'):
            attendances = attendances.filter(date__lte=data['date_to'])
        if data.get('employee'):
            attendances = attendances.filter(employee=data['employee'])
        if data.get('department'):
            attendances = attendances.filter(employee__department=data['department'])
        if data.get('status'):
            attendances = attendances.filter(status=data['status'])
    else:
        today = date.today()
        attendances = attendances.filter(date=today)

    status_counts = {
        'present': attendances.filter(status='present').count(),
        'late': attendances.filter(status='late').count(),
        'absent': attendances.filter(status='absent').count(),
        'overtime': attendances.filter(status='overtime').count(),
    }
    attendances = attendances.order_by('-date', 'employee__last_name')[:200]
    return render(request, 'core/attendance_list.html', {
        'attendances': attendances, 'form': form, 'status_counts': status_counts
    })


@login_required
@staff_required
def attendance_create(request):
    form = AttendanceForm(request.POST or None)
    if form.is_valid():
        attendance = form.save(commit=False)
        attendance.created_by = request.user
        attendance.calculate_minutes()
        attendance.save()
        messages.success(request, "Davomat muvaffaqiyatli qo'shildi!")
        return redirect('attendance_list')
    return render(request, 'core/attendance_form.html', {'form': form, 'title': "Davomat qo'shish"})


@login_required
@staff_required
def attendance_edit(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    form = AttendanceForm(request.POST or None, instance=attendance)
    if form.is_valid():
        att = form.save(commit=False)
        att.calculate_minutes()
        att.save()
        messages.success(request, "Davomat muvaffaqiyatli yangilandi!")
        return redirect('attendance_list')
    return render(request, 'core/attendance_form.html', {'form': form, 'title': "Davomatni tahrirlash", 'obj': attendance})


@login_required
@staff_required
def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, "Davomat o'chirildi!")
        return redirect('attendance_list')
    return render(request, 'core/confirm_delete.html', {'obj': attendance, 'title': "Davomatni o'chirish"})


@login_required
@staff_required
def bulk_attendance(request):
    """Add attendance for all employees for a specific date."""
    if request.method == 'POST':
        att_date = request.POST.get('date')
        from datetime import datetime as dt
        att_date = dt.strptime(att_date, '%Y-%m-%d').date()
        employees = Employee.objects.filter(is_active=True)
        created = 0
        for emp in employees:
            status = request.POST.get(f'status_{emp.id}', 'present')
            check_in = request.POST.get(f'check_in_{emp.id}') or None
            check_out = request.POST.get(f'check_out_{emp.id}') or None
            obj, created_flag = Attendance.objects.get_or_create(
                employee=emp, date=att_date,
                defaults={
                    'status': status,
                    'check_in': check_in,
                    'check_out': check_out,
                    'created_by': request.user
                }
            )
            if created_flag:
                obj.calculate_minutes()
                obj.save()
                created += 1
        messages.success(request, f"{created} ta davomat yozuvi qo'shildi!")
        return redirect('attendance_list')

    today = date.today()
    att_date_str = request.GET.get('date', today.strftime('%Y-%m-%d'))
    employees = Employee.objects.filter(is_active=True).select_related('department', 'position', 'work_schedule')
    existing_qs = Attendance.objects.filter(date=att_date_str)
    existing = set(a.employee_id for a in existing_qs)
    return render(request, 'core/bulk_attendance.html', {
        'employees': employees, 'date': att_date_str, 'existing': existing,
        'status_choices': Attendance.STATUS_CHOICES
    })


# ========== PAYROLL ==========
@login_required
@staff_required
def payroll_list(request):
    today = date.today()
    form = PayrollFilterForm(request.GET or {'month': today.month, 'year': today.year})
    payrolls = Payroll.objects.select_related('employee', 'employee__department', 'employee__position')

    month = today.month
    year = today.year
    if form.is_valid():
        month = int(form.cleaned_data['month'])
        year = form.cleaned_data['year']
        payrolls = payrolls.filter(month=month, year=year)
        if form.cleaned_data.get('department'):
            payrolls = payrolls.filter(employee__department=form.cleaned_data['department'])
    else:
        payrolls = payrolls.filter(month=month, year=year)

    totals = payrolls.aggregate(
        total_base=Sum('base_salary'),
        total_deduction=Sum('total_deduction'),
        total_overtime=Sum('overtime_pay'),
        total_net=Sum('net_salary'),
    )

    return render(request, 'core/payroll_list.html', {
        'payrolls': payrolls, 'form': form, 'totals': totals, 'month': month, 'year': year
    })


@login_required
@staff_required
def payroll_calculate(request):
    """Calculate payroll for all active employees for a given month/year."""
    today = date.today()
    month = int(request.POST.get('month', today.month))
    year = int(request.POST.get('year', today.year))

    employees = Employee.objects.filter(is_active=True)
    calculated = 0

    # Get working days in the month
    cal = calendar.monthcalendar(year, month)
    total_working_days = 0

    for employee in employees:
        attendances = Attendance.objects.filter(employee=employee, date__year=year, date__month=month)

        # Count stats
        present_days = attendances.filter(status__in=['present', 'overtime', 'incomplete']).count()
        late_days = attendances.filter(status='late').count()
        absent_days = attendances.filter(status='absent').count()
        present_days += late_days  # Late still counts as present

        total_late_minutes = attendances.aggregate(total=Sum('late_minutes'))['total'] or 0
        total_early_minutes = attendances.aggregate(total=Sum('early_leave_minutes'))['total'] or 0
        total_overtime_minutes = attendances.aggregate(total=Sum('overtime_minutes'))['total'] or 0

        base_salary = employee.salary
        daily_rate = base_salary / Decimal('26') if base_salary > 0 else Decimal('0')
        hourly_rate = employee.hourly_rate if employee.hourly_rate else (daily_rate / Decimal('8'))

        # Deductions
        # Late: 0.5% of daily rate per 30 minutes late
        late_deduction = (Decimal(total_late_minutes) / Decimal('30')) * (daily_rate * Decimal('0.005'))
        # Early leave: proportional hourly deduction
        early_leave_deduction = (Decimal(total_early_minutes) / 60) * hourly_rate
        # Absence: full daily rate per absent day
        absence_deduction = Decimal(absent_days) * daily_rate

        total_deduction = late_deduction + early_leave_deduction + absence_deduction

        # Overtime: 1.5x hourly rate
        overtime_hours = Decimal(total_overtime_minutes) / 60
        overtime_pay = overtime_hours * hourly_rate * Decimal('1.5')

        net_salary = base_salary - total_deduction + overtime_pay
        if net_salary < 0:
            net_salary = Decimal('0')

        payroll, created = Payroll.objects.update_or_create(
            employee=employee, month=month, year=year,
            defaults={
                'base_salary': base_salary,
                'working_days': 26,
                'present_days': present_days,
                'absent_days': absent_days,
                'late_count': late_days,
                'late_deduction': late_deduction,
                'early_leave_count': attendances.filter(early_leave_minutes__gt=0).count(),
                'early_leave_deduction': early_leave_deduction,
                'absence_deduction': absence_deduction,
                'overtime_hours': overtime_hours,
                'overtime_pay': overtime_pay,
                'total_deduction': total_deduction,
                'net_salary': net_salary,
                'status': 'calculated',
            }
        )
        calculated += 1

    messages.success(request, f"{calculated} ta xodim uchun ish haqi hisoblandi!")
    return redirect(f'/payroll/?month={month}&year={year}')


@login_required
@staff_required
def payroll_detail(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    attendances = Attendance.objects.filter(
        employee=payroll.employee, date__year=payroll.year, date__month=payroll.month
    ).order_by('date')
    return render(request, 'core/payroll_detail.html', {'payroll': payroll, 'attendances': attendances})


@login_required
@staff_required
def payroll_mark_paid(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    payroll.status = 'paid'
    payroll.save()
    messages.success(request, "Ish haqi to'langan deb belgilandi!")
    return redirect('payroll_list')


# ========== REPORTS ==========
@login_required
@staff_required
def reports(request):
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    # Attendance by status for the month
    month_attendances = Attendance.objects.filter(date__year=year, date__month=month)
    status_data = {}
    for status, label in Attendance.STATUS_CHOICES:
        status_data[label] = month_attendances.filter(status=status).count()

    status_labels = list(status_data.keys())
    status_values = list(status_data.values())

    # Department payroll
    dept_payroll = []
    for dept in Department.objects.all():
        total = Payroll.objects.filter(
            month=month, year=year, employee__department=dept
        ).aggregate(total=Sum('net_salary'))['total'] or 0
        if total > 0:
            dept_payroll.append({'name': dept.name, 'total': float(total)})

    # Monthly payroll trend (last 6 months)
    payroll_trend = []
    for i in range(5, -1, -1):
        d = today.replace(day=1) - timedelta(days=i * 30)
        m, y = d.month, d.year
        total = Payroll.objects.filter(month=m, year=y).aggregate(total=Sum('net_salary'))['total'] or 0
        payroll_trend.append({'month': f"{m}/{y}", 'total': float(total)})

    # Employee stats
    total_employees = Employee.objects.filter(is_active=True).count()
    by_dept = Department.objects.annotate(
        emp_count=Count('employees', filter=Q(employees__is_active=True))
    ).filter(emp_count__gt=0)

    MONTHS = {1: 'Yanvar', 2: 'Fevral', 3: 'Mart', 4: 'Aprel',
              5: 'May', 6: 'Iyun', 7: 'Iyul', 8: 'Avgust',
              9: 'Sentabr', 10: 'Oktabr', 11: 'Noyabr', 12: 'Dekabr'}

    context = {
        'month': month, 'year': year,
        'month_name': MONTHS.get(month, ''),
        'status_data': status_data,
        'status_labels': json.dumps(status_labels, ensure_ascii=False),
        'status_values': json.dumps(status_values),
        'dept_payroll': json.dumps(dept_payroll, ensure_ascii=False),
        'has_dept_payroll': len(dept_payroll) > 0,
        'payroll_trend': json.dumps(payroll_trend, ensure_ascii=False),
        'total_employees': total_employees,
        'by_dept': by_dept,
        'months': MONTHS,
        'current_year': today.year,
    }
    return render(request, 'core/reports.html', context)

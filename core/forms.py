from datetime import date
from django import forms
from .models import Department, Position, WorkSchedule, WeeklyWorkDays, Employee, Attendance, Payroll


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Bo'lim nomini kiriting"}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {'name': "Bo'lim nomi", 'description': 'Tavsif'}


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name', 'department', 'base_salary', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'base_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'Lavozim nomi', 'department': "Bo'lim",
            'base_salary': 'Asosiy maosh', 'description': 'Tavsif'
        }


class WorkScheduleForm(forms.ModelForm):
    class Meta:
        model = WorkSchedule
        fields = ['name', 'start_time', 'end_time', 'late_tolerance_minutes', 'overtime_threshold_minutes', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'late_tolerance_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'overtime_threshold_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'Jadval nomi', 'start_time': 'Ish boshlanish vaqti',
            'end_time': 'Ish tugash vaqti', 'late_tolerance_minutes': 'Kechikish chegarasi (daqiqa)',
            'overtime_threshold_minutes': "Qo'shimcha ish chegarasi (daqiqa)",
        }


class WeeklyWorkDayForm(forms.ModelForm):
    class Meta:
        model = WeeklyWorkDays
        fields = ['day_of_week', 'is_working']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'is_working': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EmployeeForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Avtomatik: employee_id'}),
        label='Login (username)',
        help_text="Bo'sh qoldirilsa, Xodim ID asosida yaratiladi"
    )
    password = forms.CharField(
        max_length=128, required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Yangi parol'}),
        label='Parol',
        help_text="Tahrirlashda bo'sh qoldirilsa, parol o'zgarmaydi"
    )

    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'middle_name', 'employee_id',
            'photo',
            'department', 'position', 'work_schedule',
            'phone', 'email', 'gender', 'hire_date', 'birth_date',
            'salary', 'hourly_rate', 'status', 'address', 'notes'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'work_schedule': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+998 90 123 45 67'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Ism', 'last_name': 'Familiya', 'middle_name': "Otasining ismi",
            'employee_id': 'Xodim ID', 'department': "Bo'lim", 'position': 'Lavozim',
            'work_schedule': 'Ish jadvali', 'phone': 'Telefon', 'email': 'Email',
            'gender': 'Jinsi', 'hire_date': 'Ishga qabul sanasi', 'birth_date': "Tug'ilgan sana",
            'salary': 'Maosh (so\'m)', 'hourly_rate': 'Soatlik stavka',
            'status': 'Holat', 'address': 'Manzil', 'notes': 'Izoh',
            'photo': 'Rasm (Face ID uchun)'
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'check_in', 'check_out', 'status', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_in': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'check_out': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'employee': 'Xodim', 'date': 'Sana', 'check_in': 'Kelish vaqti',
            'check_out': 'Ketish vaqti', 'status': 'Holat', 'notes': 'Izoh'
        }


class AttendanceFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Dan'
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Gacha'
    )
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(is_active=True),
        required=False,
        empty_label='Barcha xodimlar',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Xodim'
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="Barcha bo'limlar",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Bo'lim"
    )
    status = forms.ChoiceField(
        choices=[('', 'Barcha holatlar')] + list(Attendance.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Holat'
    )


class PayrollFilterForm(forms.Form):
    MONTH_CHOICES = [
        (1, 'Yanvar'), (2, 'Fevral'), (3, 'Mart'), (4, 'Aprel'),
        (5, 'May'), (6, 'Iyun'), (7, 'Iyul'), (8, 'Avgust'),
        (9, 'Sentabr'), (10, 'Oktabr'), (11, 'Noyabr'), (12, 'Dekabr')
    ]
    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Oy'
    )
    year = forms.IntegerField(
        initial=date.today().year,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Yil'
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="Barcha bo'limlar",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Bo'lim"
    )

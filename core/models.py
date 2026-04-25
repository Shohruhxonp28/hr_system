from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="Bo'lim nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bo'lim"
        verbose_name_plural = "Bo'limlar"
        ordering = ['name']

    def __str__(self):
        return self.name

    def employee_count(self):
        return self.employees.filter(is_active=True).count()


class Position(models.Model):
    name = models.CharField(max_length=100, verbose_name="Lavozim nomi")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='positions', verbose_name="Bo'lim")
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Asosiy maosh")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Lavozim"
        verbose_name_plural = "Lavozimlar"
        ordering = ['name']

    def __str__(self):
        return self.name


class WorkSchedule(models.Model):
    name = models.CharField(max_length=100, verbose_name="Jadval nomi")
    start_time = models.TimeField(verbose_name="Ish boshlanish vaqti")
    end_time = models.TimeField(verbose_name="Ish tugash vaqti")
    late_tolerance_minutes = models.IntegerField(default=15, verbose_name="Kechikish chegarasi (daqiqa)")
    overtime_threshold_minutes = models.IntegerField(default=30, verbose_name="Qo'shimcha ish chegarasi (daqiqa)")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Ish jadvali"
        verbose_name_plural = "Ish jadvallari"

    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"


class WeeklyWorkDays(models.Model):
    DAYS = [
        (0, 'Dushanba'),
        (1, 'Seshanba'),
        (2, 'Chorshanba'),
        (3, 'Payshanba'),
        (4, 'Juma'),
        (5, 'Shanba'),
        (6, 'Yakshanba'),
    ]
    schedule = models.ForeignKey(WorkSchedule, on_delete=models.CASCADE, related_name='work_days')
    day_of_week = models.IntegerField(choices=DAYS, verbose_name="Hafta kuni")
    is_working = models.BooleanField(default=True, verbose_name="Ish kuni")

    class Meta:
        unique_together = ('schedule', 'day_of_week')
        ordering = ['day_of_week']

    def __str__(self):
        return f"{self.schedule.name} - {self.get_day_of_week_display()}"


class Employee(models.Model):
    GENDER_CHOICES = [('M', 'Erkak'), ('F', 'Ayol')]
    STATUS_CHOICES = [('active', 'Faol'), ('inactive', 'Nofaol'), ('on_leave', "Ta'tilda")]

    first_name = models.CharField(max_length=100, verbose_name="Ism")
    last_name = models.CharField(max_length=100, verbose_name="Familiya")
    middle_name = models.CharField(max_length=100, blank=True, verbose_name="Otasining ismi")
    employee_id = models.CharField(max_length=20, unique=True, verbose_name="Xodim ID")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True,
                                   related_name='employees', verbose_name="Bo'lim")
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True,
                                 related_name='employees', verbose_name="Lavozim")
    work_schedule = models.ForeignKey(WorkSchedule, on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name="Ish jadvali")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    email = models.EmailField(blank=True, verbose_name="Email")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M', verbose_name="Jinsi")
    hire_date = models.DateField(verbose_name="Ishga qabul sanasi")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Tug'ilgan sana")
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Maosh")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Soatlik stavka")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Holat")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    address = models.TextField(blank=True, verbose_name="Manzil")
    notes = models.TextField(blank=True, verbose_name="Izoh")
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_profile', verbose_name="Foydalanuvchi")
    photo = models.ImageField(upload_to='employee_photos/', null=True, blank=True, verbose_name="Rasm (Face ID uchun)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Xodim"
        verbose_name_plural = "Xodimlar"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Vaqtida keldi'),
        ('late', 'Kechikdi'),
        ('absent', 'Kelmadi'),
        ('day_off', 'Dam olish kuni'),
        ('holiday', 'Bayram kuni'),
        ('incomplete', "To'liq emas"),
        ('overtime', "Qo'shimcha ish"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                                 related_name='attendances', verbose_name="Xodim")
    date = models.DateField(verbose_name="Sana")
    check_in = models.TimeField(null=True, blank=True, verbose_name="Kelish vaqti")
    check_out = models.TimeField(null=True, blank=True, verbose_name="Ketish vaqti")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present', verbose_name="Holat")
    late_minutes = models.IntegerField(default=0, verbose_name="Kechikish (daqiqa)")
    early_leave_minutes = models.IntegerField(default=0, verbose_name="Erta ketish (daqiqa)")
    overtime_minutes = models.IntegerField(default=0, verbose_name="Qo'shimcha ish (daqiqa)")
    notes = models.TextField(blank=True, verbose_name="Izoh")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Davomat"
        verbose_name_plural = "Davomat"
        unique_together = ('employee', 'date')
        ordering = ['-date', 'employee__last_name']

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.get_status_display()}"

    def calculate_minutes(self):
        """Calculate late, early leave, and overtime minutes based on schedule."""
        employee = self.employee
        if not employee.work_schedule:
            return
        schedule = employee.work_schedule
        if self.check_in and self.status not in ('absent', 'day_off', 'holiday'):
            from datetime import datetime, date
            base = date.today()
            check_in_dt = datetime.combine(base, self.check_in)
            scheduled_start = datetime.combine(base, schedule.start_time)
            if check_in_dt > scheduled_start:
                diff = int((check_in_dt - scheduled_start).total_seconds() / 60)
                if diff > schedule.late_tolerance_minutes:
                    self.late_minutes = diff
                    if self.status == 'present':
                        self.status = 'late'
        if self.check_out and self.status not in ('absent', 'day_off', 'holiday'):
            from datetime import datetime, date
            base = date.today()
            check_out_dt = datetime.combine(base, self.check_out)
            scheduled_end = datetime.combine(base, schedule.end_time)
            if check_out_dt < scheduled_end:
                diff = int((scheduled_end - check_out_dt).total_seconds() / 60)
                self.early_leave_minutes = diff
                if diff > 30:
                    self.status = 'incomplete'
            elif check_out_dt > scheduled_end:
                diff = int((check_out_dt - scheduled_end).total_seconds() / 60)
                if diff >= schedule.overtime_threshold_minutes:
                    self.overtime_minutes = diff
                    if self.status == 'present':
                        self.status = 'overtime'


class Payroll(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Qoralama'),
        ('calculated', 'Hisoblangan'),
        ('paid', "To'langan"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                                 related_name='payrolls', verbose_name="Xodim")
    month = models.IntegerField(verbose_name="Oy")
    year = models.IntegerField(verbose_name="Yil")
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Asosiy maosh")
    working_days = models.IntegerField(default=0, verbose_name="Ish kunlari")
    present_days = models.IntegerField(default=0, verbose_name="Kelgan kunlar")
    absent_days = models.IntegerField(default=0, verbose_name="Kelmagan kunlar")
    late_count = models.IntegerField(default=0, verbose_name="Kechikishlar soni")
    late_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Kechikish uchun ayirish")
    early_leave_count = models.IntegerField(default=0, verbose_name="Erta ketishlar soni")
    early_leave_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Erta ketish uchun ayirish")
    absence_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Kelmagan kun uchun ayirish")
    overtime_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Qo'shimcha ish soatlari")
    overtime_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Qo'shimcha ish haqi")
    total_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Jami ayirish")
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Jami maosh")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Holat")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ish haqi"
        verbose_name_plural = "Ish haqilari"
        unique_together = ('employee', 'month', 'year')
        ordering = ['-year', '-month', 'employee__last_name']

    def __str__(self):
        return f"{self.employee} - {self.month}/{self.year}"

    MONTH_NAMES = {
        1: 'Yanvar', 2: 'Fevral', 3: 'Mart', 4: 'Aprel',
        5: 'May', 6: 'Iyun', 7: 'Iyul', 8: 'Avgust',
        9: 'Sentabr', 10: 'Oktabr', 11: 'Noyabr', 12: 'Dekabr'
    }

    def month_name(self):
        return self.MONTH_NAMES.get(self.month, str(self.month))

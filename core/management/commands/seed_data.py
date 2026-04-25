from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Department, Position, WorkSchedule, WeeklyWorkDays, Employee, Attendance, Payroll
from datetime import date, time, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = "Namuna ma'lumotlarini yuklash"

    def handle(self, *args, **options):
        self.stdout.write("Ma'lumotlar yuklanmoqda...")

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@hrms.uz', 'admin123')
            self.stdout.write(self.style.SUCCESS("✓ Admin foydalanuvchi yaratildi (admin / admin123)"))

        # Departments
        depts_data = [
            ("Moliya bo'limi", "Moliyaviy hisobot va byudjet boshqaruvi"),
            ("IT bo'limi", "Axborot texnologiyalari va tizim boshqaruvi"),
            ("Marketing bo'limi", "Reklama, brending va savdo strategiyasi"),
            ("HR bo'limi", "Kadrlar boshqaruvi va rivojlantirish"),
            ("Ishlab chiqarish", "Mahsulot ishlab chiqarish va sifat nazorati"),
        ]
        departments = {}
        for name, desc in depts_data:
            d, _ = Department.objects.get_or_create(name=name, defaults={'description': desc})
            departments[name] = d
        self.stdout.write(self.style.SUCCESS(f"✓ {len(departments)} ta bo'lim yaratildi"))

        # Work Schedules
        schedule_standard, _ = WorkSchedule.objects.get_or_create(
            name="Standart (9:00 - 18:00)",
            defaults={
                'start_time': time(9, 0),
                'end_time': time(18, 0),
                'late_tolerance_minutes': 15,
                'overtime_threshold_minutes': 30,
            }
        )
        schedule_early, _ = WorkSchedule.objects.get_or_create(
            name="Erta (8:00 - 17:00)",
            defaults={
                'start_time': time(8, 0),
                'end_time': time(17, 0),
                'late_tolerance_minutes': 10,
                'overtime_threshold_minutes': 30,
            }
        )
        schedule_late, _ = WorkSchedule.objects.get_or_create(
            name="Kech (10:00 - 19:00)",
            defaults={
                'start_time': time(10, 0),
                'end_time': time(19, 0),
                'late_tolerance_minutes': 15,
                'overtime_threshold_minutes': 30,
            }
        )
        schedules = [schedule_standard, schedule_early, schedule_late]

        # Weekly work days for each schedule (Mon-Fri)
        for schedule in schedules:
            for day_num in range(7):
                WeeklyWorkDays.objects.get_or_create(
                    schedule=schedule,
                    day_of_week=day_num,
                    defaults={'is_working': day_num < 5}
                )
        self.stdout.write(self.style.SUCCESS("✓ Ish jadvallari yaratildi"))

        # Positions
        positions_data = [
            ("Bosh moliyachi (CFO)", departments["Moliya bo'limi"], 12000000),
            ("Moliyachi", departments["Moliya bo'limi"], 7500000),
            ("Buxgalter", departments["Moliya bo'limi"], 6000000),
            ("IT direktor (CTO)", departments["IT bo'limi"], 15000000),
            ("Dasturchi (Senior)", departments["IT bo'limi"], 12000000),
            ("Dasturchi (Junior)", departments["IT bo'limi"], 7000000),
            ("Tizim administratori", departments["IT bo'limi"], 8000000),
            ("Marketing direktori", departments["Marketing bo'limi"], 11000000),
            ("SMM mutaxassis", departments["Marketing bo'limi"], 6500000),
            ("Dizayner", departments["Marketing bo'limi"], 7000000),
            ("HR menejer", departments["HR bo'limi"], 9000000),
            ("HR mutaxassis", departments["HR bo'limi"], 6000000),
            ("Ishlab chiqarish boshlig'i", departments["Ishlab chiqarish"], 10000000),
            ("Texnolog", departments["Ishlab chiqarish"], 7000000),
            ("Operator", departments["Ishlab chiqarish"], 5000000),
        ]
        positions = {}
        for name, dept, salary in positions_data:
            p, _ = Position.objects.get_or_create(
                name=name,
                defaults={'department': dept, 'base_salary': Decimal(salary)}
            )
            positions[name] = p
        self.stdout.write(self.style.SUCCESS(f"✓ {len(positions)} ta lavozim yaratildi"))

        # Employees
        employees_data = [
            ("Karimov", "Alisher", "Baxtiyorovich", "EMP001", departments["IT bo'limi"], positions["Dasturchi (Senior)"], schedule_standard, "+998901234567", 12000000),
            ("Rahimova", "Dilnoza", "Hamidovna", "EMP002", departments["IT bo'limi"], positions["Dasturchi (Junior)"], schedule_standard, "+998912345678", 7000000),
            ("Toshmatov", "Bobur", "Ergashevich", "EMP003", departments["Moliya bo'limi"], positions["Buxgalter"], schedule_early, "+998903456789", 6000000),
            ("Yusupova", "Gulnora", "Mirzayevna", "EMP004", departments["HR bo'limi"], positions["HR menejer"], schedule_standard, "+998904567890", 9000000),
            ("Nazarov", "Jasur", "Olimovich", "EMP005", departments["Marketing bo'limi"], positions["SMM mutaxassis"], schedule_late, "+998905678901", 6500000),
            ("Mirzayev", "Sardor", "Toxirovich", "EMP006", departments["IT bo'limi"], positions["Tizim administratori"], schedule_standard, "+998906789012", 8000000),
            ("Xasanova", "Madina", "Botirov", "EMP007", departments["Marketing bo'limi"], positions["Dizayner"], schedule_late, "+998907890123", 7000000),
            ("Ergashev", "Ulugbek", "Sobirovich", "EMP008", departments["Ishlab chiqarish"], positions["Operator"], schedule_early, "+998908901234", 5000000),
            ("Qodirov", "Firdavs", "Hamroyevich", "EMP009", departments["Moliya bo'limi"], positions["Moliyachi"], schedule_standard, "+998909012345", 7500000),
            ("Sultanova", "Zulfiya", "Normatovna", "EMP010", departments["HR bo'limi"], positions["HR mutaxassis"], schedule_standard, "+998901122334", 6000000),
            ("Hamidov", "Otabek", "Ravshanov", "EMP011", departments["IT bo'limi"], positions["Dasturchi (Senior)"], schedule_standard, "+998902233445", 12000000),
            ("Normatova", "Shahnoza", "Aliyevna", "EMP012", departments["Marketing bo'limi"], positions["Marketing direktori"], schedule_standard, "+998903344556", 11000000),
            ("Rashidov", "Sanjar", "Komilovich", "EMP013", departments["Ishlab chiqarish"], positions["Texnolog"], schedule_early, "+998904455667", 7000000),
            ("Tursunov", "Bahodir", "Umarov", "EMP014", departments["Moliya bo'limi"], positions["Bosh moliyachi (CFO)"], schedule_standard, "+998905566778", 12000000),
            ("Aminova", "Feruza", "Sotvoldiyevna", "EMP015", departments["IT bo'limi"], positions["IT direktor (CTO)"], schedule_standard, "+998906677889", 15000000),
        ]

        employees = []
        employee_user_count = 0
        for lname, fname, mname, emp_id, dept, pos, sched, phone, salary in employees_data:
            # Demo uchun har bir xodimga alohida login yaratiladi.
            # Masalan: EMP001 -> login: emp001, parol: emp001123
            username = emp_id.lower()
            password = f"{username}123"

            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': fname,
                    'last_name': lname,
                    'email': f"{username}@hrms.local",
                    'is_staff': False,
                    'is_superuser': False,
                }
            )
            if user_created:
                user.set_password(password)
                user.save()
                employee_user_count += 1
            else:
                # Ism/familiya o'zgargan bo'lsa, yangilab qo'yamiz. Parolni reset qilmaymiz.
                changed = False
                if user.first_name != fname:
                    user.first_name = fname
                    changed = True
                if user.last_name != lname:
                    user.last_name = lname
                    changed = True
                if changed:
                    user.save()

            emp, created = Employee.objects.get_or_create(
                employee_id=emp_id,
                defaults={
                    'first_name': fname,
                    'last_name': lname,
                    'middle_name': mname,
                    'department': dept,
                    'position': pos,
                    'work_schedule': sched,
                    'phone': phone,
                    'salary': Decimal(salary),
                    'hourly_rate': Decimal(salary) / 26 / 8,
                    'hire_date': date(2022, random.randint(1, 12), random.randint(1, 28)),
                    'gender': random.choice(['M', 'F']),
                    'status': 'active',
                    'is_active': True,
                    'user': user,
                }
            )

            # Agar xodim oldindan bor bo'lib, user ulanmagan bo'lsa, bog'lab qo'yamiz.
            if not emp.user:
                emp.user = user
                emp.save(update_fields=['user'])

            employees.append(emp)
        self.stdout.write(self.style.SUCCESS(f"✓ {len(employees)} ta xodim yaratildi/yuklandi"))
        self.stdout.write(self.style.SUCCESS(f"✓ {employee_user_count} ta xodim loginlari yaratildi"))

        # Generate attendance for last 30 days
        today = date.today()
        attendance_count = 0
        status_pool = ['present', 'present', 'present', 'present', 'late', 'late', 'absent', 'incomplete', 'overtime']

        for emp in employees:
            schedule = emp.work_schedule
            if not schedule:
                continue

            for day_offset in range(30, -1, -1):
                att_date = today - timedelta(days=day_offset)
                weekday = att_date.weekday()  # 0=Mon, 6=Sun

                # Check if working day
                work_day = WeeklyWorkDays.objects.filter(schedule=schedule, day_of_week=weekday).first()
                if work_day and not work_day.is_working:
                    Attendance.objects.get_or_create(
                        employee=emp, date=att_date,
                        defaults={'status': 'day_off'}
                    )
                    continue

                status = random.choice(status_pool)
                check_in = None
                check_out = None
                late_min = 0
                early_leave_min = 0
                overtime_min = 0

                from datetime import datetime as dt, timedelta as td
                base_in = dt.combine(att_date, schedule.start_time)
                base_out = dt.combine(att_date, schedule.end_time)

                if status == 'present':
                    check_in = (base_in + td(minutes=random.randint(-5, 10))).time()
                    check_out = (base_out + td(minutes=random.randint(-10, 20))).time()
                elif status == 'late':
                    late_min = random.randint(20, 90)
                    check_in = (base_in + td(minutes=late_min)).time()
                    check_out = (base_out + td(minutes=random.randint(0, 30))).time()
                elif status == 'absent':
                    check_in = None
                    check_out = None
                elif status == 'incomplete':
                    check_in = (base_in + td(minutes=random.randint(-5, 15))).time()
                    early_leave_min = random.randint(40, 120)
                    check_out = (base_out - td(minutes=early_leave_min)).time()
                elif status == 'overtime':
                    check_in = (base_in + td(minutes=random.randint(-5, 10))).time()
                    overtime_min = random.randint(45, 180)
                    check_out = (base_out + td(minutes=overtime_min)).time()

                _, created = Attendance.objects.get_or_create(
                    employee=emp,
                    date=att_date,
                    defaults={
                        'check_in': check_in,
                        'check_out': check_out,
                        'status': status,
                        'late_minutes': late_min,
                        'early_leave_minutes': early_leave_min,
                        'overtime_minutes': overtime_min,
                    }
                )
                if created:
                    attendance_count += 1

        self.stdout.write(self.style.SUCCESS(f"✓ {attendance_count} ta davomat yozuvi yaratildi"))

        # Generate payroll for last 3 months
        payroll_count = 0
        for month_offset in range(3, -1, -1):
            ref_date = today.replace(day=1) - timedelta(days=month_offset * 30)
            m, y = ref_date.month, ref_date.year

            for emp in employees:
                attendances = Attendance.objects.filter(employee=emp, date__year=y, date__month=m)
                if not attendances.exists():
                    continue

                present = attendances.filter(status__in=['present', 'overtime', 'incomplete']).count()
                late_days = attendances.filter(status='late').count()
                present += late_days
                absent = attendances.filter(status='absent').count()

                total_late = sum(a.late_minutes for a in attendances)
                total_early = sum(a.early_leave_minutes for a in attendances)
                total_overtime = sum(a.overtime_minutes for a in attendances)

                base_salary = emp.salary
                daily_rate = base_salary / 26 if base_salary > 0 else Decimal('0')
                hourly_rate = emp.hourly_rate or (daily_rate / 8)

                late_deduction = (Decimal(total_late) / 30) * (daily_rate * Decimal('0.005'))
                early_deduction = (Decimal(total_early) / 60) * hourly_rate
                absence_deduction = Decimal(absent) * daily_rate
                total_deduction = late_deduction + early_deduction + absence_deduction

                overtime_hours = Decimal(total_overtime) / 60
                overtime_pay = overtime_hours * hourly_rate * Decimal('1.5')

                net = base_salary - total_deduction + overtime_pay
                if net < 0:
                    net = Decimal('0')

                status = 'paid' if month_offset > 0 else 'calculated'

                _, created = Payroll.objects.get_or_create(
                    employee=emp, month=m, year=y,
                    defaults={
                        'base_salary': base_salary,
                        'working_days': 26,
                        'present_days': present,
                        'absent_days': absent,
                        'late_count': late_days,
                        'late_deduction': late_deduction,
                        'early_leave_count': attendances.filter(early_leave_minutes__gt=0).count(),
                        'early_leave_deduction': early_deduction,
                        'absence_deduction': absence_deduction,
                        'overtime_hours': overtime_hours,
                        'overtime_pay': overtime_pay,
                        'total_deduction': total_deduction,
                        'net_salary': net,
                        'status': status,
                    }
                )
                if created:
                    payroll_count += 1

        self.stdout.write(self.style.SUCCESS(f"✓ {payroll_count} ta ish haqi yozuvi yaratildi"))
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(self.style.SUCCESS("✅ Barcha ma'lumotlar muvaffaqiyatli yuklandi!"))
        self.stdout.write(self.style.SUCCESS("   URL: http://127.0.0.1:8000"))
        self.stdout.write(self.style.SUCCESS("   Admin login: admin"))
        self.stdout.write(self.style.SUCCESS("   Admin parol: admin123"))
        self.stdout.write(self.style.SUCCESS("   Xodim demo login: emp001"))
        self.stdout.write(self.style.SUCCESS("   Xodim demo parol: emp001123"))
        self.stdout.write(self.style.SUCCESS("=" * 50))

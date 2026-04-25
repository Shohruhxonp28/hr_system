import json
import base64
import os
import numpy as np
import cv2
from datetime import date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from django.core.files.base import ContentFile
from .models import Employee, Attendance, Payroll
import calendar

@login_required
def employee_dashboard(request):
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Siz xodim emassiz!")
        return redirect('dashboard')

    today = date.today()
    attendance = Attendance.objects.filter(employee=employee, date=today).first()
    
    schedule = employee.work_schedule
    recent_attendances = Attendance.objects.filter(employee=employee).order_by('-date')[:5]

    context = {
        'employee': employee,
        'today': today,
        'attendance': attendance,
        'schedule': schedule,
        'recent_attendances': recent_attendances,
    }
    return render(request, 'core/employee_panel/dashboard.html', context)


@login_required
def employee_attendance(request):
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        return redirect('dashboard')

    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    
    attendances = Attendance.objects.filter(employee=employee, date__month=month, date__year=year).order_by('-date')
    
    status_filter = request.GET.get('status')
    if status_filter:
        attendances = attendances.filter(status=status_filter)

    months = {1: 'Yanvar', 2: 'Fevral', 3: 'Mart', 4: 'Aprel', 5: 'May', 6: 'Iyun', 
              7: 'Iyul', 8: 'Avgust', 9: 'Sentabr', 10: 'Oktabr', 11: 'Noyabr', 12: 'Dekabr'}

    return render(request, 'core/employee_panel/attendance.html', {
        'employee': employee,
        'attendances': attendances,
        'month': month,
        'year': year,
        'months': months,
        'status_choices': Attendance.STATUS_CHOICES,
        'status_filter': status_filter
    })

@login_required
def employee_calendar(request):
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        return redirect('dashboard')

    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    attendances = Attendance.objects.filter(employee=employee, date__month=month, date__year=year)
    att_dict = {att.date.day: att for att in attendances}

    cal = calendar.monthcalendar(year, month)
    
    months = {1: 'Yanvar', 2: 'Fevral', 3: 'Mart', 4: 'Aprel', 5: 'May', 6: 'Iyun', 
              7: 'Iyul', 8: 'Avgust', 9: 'Sentabr', 10: 'Oktabr', 11: 'Noyabr', 12: 'Dekabr'}

    return render(request, 'core/employee_panel/calendar.html', {
        'employee': employee,
        'cal': cal,
        'att_dict': att_dict,
        'month': month,
        'year': year,
        'months': months
    })

@login_required
def employee_salary(request):
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        return redirect('dashboard')

    today = date.today()
    year = int(request.GET.get('year', today.year))
    
    payrolls = Payroll.objects.filter(employee=employee, year=year).order_by('-month')

    return render(request, 'core/employee_panel/salary.html', {
        'employee': employee,
        'payrolls': payrolls,
        'year': year,
    })

@login_required
def employee_profile(request):
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        return redirect('dashboard')

    if request.method == 'POST':
        # Simple change password
        new_password = request.POST.get('new_password')
        if new_password:
            request.user.set_password(new_password)
            request.user.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(request, "Parol muvaffaqiyatli o'zgartirildi!")
            return redirect('employee_profile')

    return render(request, 'core/employee_panel/profile.html', {
        'employee': employee,
    })


@login_required
def employee_upload_photo(request):
    """Xodim profildan rasm faylini yuklashi"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        return redirect('dashboard')

    if request.method == 'POST' and request.FILES.get('photo'):
        employee.photo = request.FILES['photo']
        employee.save()
        messages.success(request, "Profil rasmi muvaffaqiyatli yuklandi!")
    else:
        messages.error(request, "Iltimos, rasm faylini tanlang.")

    return redirect('employee_profile')


@login_required
def employee_capture_photo(request):
    """Kameradan olingan rasmni saqlash"""
    if request.method == 'POST':
        try:
            employee = request.user.employee_profile
            data = json.loads(request.body)
            image_data = data.get('image')

            if not image_data:
                return JsonResponse({'success': False, 'message': "Rasm topilmadi"})

            # Base64 rasmni decode qilish
            fmt, imgstr = image_data.split(';base64,')
            ext = fmt.split('/')[-1]
            img_bytes = base64.b64decode(imgstr)

            # Yuz borligini tekshirish
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            if len(faces) == 0:
                return JsonResponse({'success': False, 'message': "Yuz topilmadi. Yuzingizni kameraga to'g'ri tutib qaytadan urinib ko'ring."})

            # Saqlash
            filename = f"employee_{employee.employee_id}.{ext}"
            employee.photo.save(filename, ContentFile(img_bytes), save=True)

            return JsonResponse({'success': True, 'message': "Rasm muvaffaqiyatli saqlandi!"})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Xatolik: {str(e)}"})

    return JsonResponse({'success': False, 'message': "Xato so'rov"})


@login_required
def face_id_scan(request):
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        return redirect('dashboard')

    if not employee.photo:
        messages.error(request, "Face ID uchun avval profilingizga rasm qo'shing.")
        return redirect('employee_profile')

    today = date.today()
    attendance = Attendance.objects.filter(employee=employee, date=today).first()
    
    if attendance and attendance.check_in and attendance.check_out:
        messages.info(request, "Bugungi davomat yakunlangan")
        return redirect('employee_dashboard')

    return render(request, 'core/employee_panel/face_id.html', {'employee': employee, 'attendance': attendance})


@login_required
def api_face_check(request):
    if request.method == 'POST':
        try:
            employee = request.user.employee_profile
            data = json.loads(request.body)
            image_data = data.get('image')
            
            if not image_data:
                return JsonResponse({'success': False, 'message': "Kameradan rasm olinmadi"})

            if not employee.photo:
                return JsonResponse({'success': False, 'message': "Profilingizda rasm yo'q. Avval profil sahifasida rasm yuklang."})

            # Kameradan olingan rasmni decode qilish
            fmt, imgstr = image_data.split(';base64,')
            img_bytes = base64.b64decode(imgstr)
            nparr = np.frombuffer(img_bytes, np.uint8)
            captured_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if captured_img is None:
                return JsonResponse({'success': False, 'message': "Rasm o'qilmadi"})

            # Kameradan yuz aniqlash
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray_cap = cv2.cvtColor(captured_img, cv2.COLOR_BGR2GRAY)
            faces_cap = face_cascade.detectMultiScale(gray_cap, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
            
            if len(faces_cap) == 0:
                return JsonResponse({'success': False, 'message': "Yuz topilmadi. Yuzingizni kameraga to'g'ri tutib qaytadan urinib ko'ring."})
            
            # Saqlangan rasmdan yuz aniqlash
            saved_img_path = employee.photo.path
            if not os.path.exists(saved_img_path):
                return JsonResponse({'success': False, 'message': "Profil rasmi topilmadi"})

            saved_img = cv2.imread(saved_img_path)
            if saved_img is None:
                return JsonResponse({'success': False, 'message': "Profil rasmi o'qilmadi"})

            gray_saved = cv2.cvtColor(saved_img, cv2.COLOR_BGR2GRAY)
            faces_saved = face_cascade.detectMultiScale(gray_saved, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))

            if len(faces_saved) == 0:
                return JsonResponse({'success': False, 'message': "Profil rasmida yuz topilmadi. Yangi rasm yuklang."})

            # ORB feature matching bilan yuzlarni solishtirish
            (x1, y1, w1, h1) = faces_cap[0]
            face_captured = gray_cap[y1:y1+h1, x1:x1+w1]
            face_captured = cv2.resize(face_captured, (200, 200))

            (x2, y2, w2, h2) = faces_saved[0]
            face_saved = gray_saved[y2:y2+h2, x2:x2+w2]
            face_saved = cv2.resize(face_saved, (200, 200))

            # Histogram solishtirish
            hist_cap = cv2.calcHist([face_captured], [0], None, [256], [0, 256])
            hist_saved = cv2.calcHist([face_saved], [0], None, [256], [0, 256])
            cv2.normalize(hist_cap, hist_cap)
            cv2.normalize(hist_saved, hist_saved)

            similarity = cv2.compareHist(hist_cap, hist_saved, cv2.HISTCMP_CORREL)

            # Demo uchun threshold past — 0.3 (haqiqiy tizimda yuqoriroq bo'ladi)
            if similarity < 0.3:
                return JsonResponse({'success': False, 'message': f"Yuz mos kelmadi (o'xshashlik: {similarity:.0%}). Qaytadan urinib ko'ring."})
            
            # Davomat saqlash
            today = date.today()
            now = timezone.localtime().time()
            
            attendance, created = Attendance.objects.get_or_create(
                employee=employee, date=today,
                defaults={'check_in': now, 'status': 'present', 'created_by': request.user}
            )
            
            if created:
                action = "Kirish"
            else:
                if attendance.check_out:
                    return JsonResponse({'success': False, 'message': "Bugungi davomat yakunlangan"})
                attendance.check_out = now
                action = "Chiqish"
            
            attendance.calculate_minutes()
            attendance.save()

            return JsonResponse({
                'success': True, 
                'message': f"{action} muvaffaqiyatli belgilandi! (o'xshashlik: {similarity:.0%})"
            })

        except Employee.DoesNotExist:
            return JsonResponse({'success': False, 'message': "Xodim topilmadi"})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Xatolik: {str(e)}"})
            
    return JsonResponse({'success': False, 'message': "Xato so'rov"})

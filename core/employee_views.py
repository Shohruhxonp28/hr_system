import base64
import calendar
import json
import os
from datetime import date

import cv2
import numpy as np
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Attendance, Employee, Payroll


MONTHS = {
    1: 'Yanvar', 2: 'Fevral', 3: 'Mart', 4: 'Aprel',
    5: 'May', 6: 'Iyun', 7: 'Iyul', 8: 'Avgust',
    9: 'Sentabr', 10: 'Oktabr', 11: 'Noyabr', 12: 'Dekabr'
}

FACE_MATCH_THRESHOLD = 0.30  # Demo uchun. Real tizimda embedding model ishlatish tavsiya qilinadi.


def _get_employee_or_redirect(request):
    """Login qilgan foydalanuvchiga bog'langan Employee obyektini qaytaradi."""
    try:
        return request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Sizga xodim profili biriktirilmagan!")
        return None


def _decode_base64_image(image_data):
    """data:image/...;base64 ko'rinishidagi rasmni OpenCV formatiga o'tkazadi."""
    if not image_data or ';base64,' not in image_data:
        return None, None, None

    fmt, imgstr = image_data.split(';base64,', 1)
    ext = fmt.split('/')[-1].lower().replace('jpeg', 'jpg')
    img_bytes = base64.b64decode(imgstr)
    nparr = np.frombuffer(img_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image, img_bytes, ext


def _largest_face(faces):
    """Topilgan yuzlar ichidan eng kattasini tanlaydi."""
    if len(faces) == 0:
        return None
    return max(faces, key=lambda item: item[2] * item[3])


def _extract_face_gray(image, face_cascade):
    """Rasmdan yuzni topadi va 200x200 grayscale yuz fragmentini qaytaradi."""
    if image is None:
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(60, 60)
    )

    face = _largest_face(faces)
    if face is None:
        return None

    x, y, w, h = face
    face_gray = gray[y:y + h, x:x + w]
    face_gray = cv2.resize(face_gray, (200, 200))
    return face_gray


def _compare_faces(face_a, face_b):
    """Demo uchun histogram correlation orqali yuz o'xshashligini hisoblaydi."""
    hist_a = cv2.calcHist([face_a], [0], None, [256], [0, 256])
    hist_b = cv2.calcHist([face_b], [0], None, [256], [0, 256])
    cv2.normalize(hist_a, hist_a)
    cv2.normalize(hist_b, hist_b)
    return cv2.compareHist(hist_a, hist_b, cv2.HISTCMP_CORREL)


def _face_cascade():
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    cascade = cv2.CascadeClassifier(cascade_path)
    if cascade.empty():
        raise RuntimeError("OpenCV face cascade yuklanmadi")
    return cascade


@login_required
def employee_dashboard(request):
    employee = _get_employee_or_redirect(request)
    if employee is None:
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
    employee = _get_employee_or_redirect(request)
    if employee is None:
        return redirect('dashboard')

    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    attendances = Attendance.objects.filter(
        employee=employee,
        date__month=month,
        date__year=year
    ).order_by('-date')

    status_filter = request.GET.get('status')
    if status_filter:
        attendances = attendances.filter(status=status_filter)

    return render(request, 'core/employee_panel/attendance.html', {
        'employee': employee,
        'attendances': attendances,
        'month': month,
        'year': year,
        'months': MONTHS,
        'status_choices': Attendance.STATUS_CHOICES,
        'status_filter': status_filter
    })


@login_required
def employee_calendar(request):
    employee = _get_employee_or_redirect(request)
    if employee is None:
        return redirect('dashboard')

    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    attendances = Attendance.objects.filter(employee=employee, date__month=month, date__year=year)
    att_dict = {att.date.day: att for att in attendances}
    cal = calendar.monthcalendar(year, month)

    return render(request, 'core/employee_panel/calendar.html', {
        'employee': employee,
        'cal': cal,
        'att_dict': att_dict,
        'month': month,
        'year': year,
        'months': MONTHS
    })


@login_required
def employee_salary(request):
    employee = _get_employee_or_redirect(request)
    if employee is None:
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
    employee = _get_employee_or_redirect(request)
    if employee is None:
        return redirect('dashboard')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        if new_password:
            request.user.set_password(new_password)
            request.user.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(request, "Parol muvaffaqiyatli o'zgartirildi!")
            return redirect('employee_profile')

    return render(request, 'core/employee_panel/profile.html', {'employee': employee})


@login_required
def employee_upload_photo(request):
    """Xodim profildan rasm faylini yuklashi."""
    employee = _get_employee_or_redirect(request)
    if employee is None:
        return redirect('dashboard')

    if request.method != 'POST' or not request.FILES.get('photo'):
        messages.error(request, "Iltimos, rasm faylini tanlang.")
        return redirect('employee_profile')

    photo = request.FILES['photo']
    employee.photo = photo
    employee.save()
    messages.success(request, "Profil rasmi muvaffaqiyatli yuklandi!")
    return redirect('employee_profile')


@login_required
def employee_capture_photo(request):
    """Kameradan olingan rasmni xodim profil rasmi sifatida saqlaydi."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': "Xato so'rov"})

    try:
        employee = request.user.employee_profile
        data = json.loads(request.body)
        image_data = data.get('image')

        image, img_bytes, ext = _decode_base64_image(image_data)
        if image is None:
            return JsonResponse({'success': False, 'message': "Rasm o'qilmadi"})

        cascade = _face_cascade()
        face = _extract_face_gray(image, cascade)
        if face is None:
            return JsonResponse({
                'success': False,
                'message': "Yuz topilmadi. Yuzingizni kameraga to'g'ri tutib qaytadan urinib ko'ring."
            })

        filename = f"employee_{employee.employee_id}.{ext or 'jpg'}"
        employee.photo.save(filename, ContentFile(img_bytes), save=True)

        return JsonResponse({'success': True, 'message': "Rasm muvaffaqiyatli saqlandi!"})

    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'message': "Xodim topilmadi"})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f"Xatolik: {str(e)}"})


@login_required
def face_id_scan(request):
    employee = _get_employee_or_redirect(request)
    if employee is None:
        return redirect('dashboard')

    if not employee.photo:
        messages.error(request, "Face ID uchun avval profilingizga rasm qo'shing.")
        return redirect('employee_profile')

    today = date.today()
    attendance = Attendance.objects.filter(employee=employee, date=today).first()

    if attendance and attendance.check_in and attendance.check_out:
        messages.info(request, "Bugungi davomat yakunlangan")
        return redirect('employee_dashboard')

    return render(request, 'core/employee_panel/face_id.html', {
        'employee': employee,
        'attendance': attendance
    })


@login_required
def api_face_check(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': "Xato so'rov"})

    try:
        employee = request.user.employee_profile
        data = json.loads(request.body)
        image_data = data.get('image')

        captured_img, _, _ = _decode_base64_image(image_data)
        if captured_img is None:
            return JsonResponse({'success': False, 'message': "Kameradan rasm olinmadi yoki rasm o'qilmadi"})

        if not employee.photo:
            return JsonResponse({
                'success': False,
                'message': "Profilingizda rasm yo'q. Avval profil sahifasida rasm yuklang."
            })

        saved_img_path = employee.photo.path
        if not os.path.exists(saved_img_path):
            return JsonResponse({'success': False, 'message': "Profil rasmi topilmadi"})

        saved_img = cv2.imread(saved_img_path)
        if saved_img is None:
            return JsonResponse({'success': False, 'message': "Profil rasmi o'qilmadi"})

        cascade = _face_cascade()
        face_captured = _extract_face_gray(captured_img, cascade)
        if face_captured is None:
            return JsonResponse({
                'success': False,
                'message': "Kameradan yuz topilmadi. Yuzingizni kameraga to'g'ri tutib qaytadan urinib ko'ring."
            })

        face_saved = _extract_face_gray(saved_img, cascade)
        if face_saved is None:
            return JsonResponse({
                'success': False,
                'message': "Profil rasmida yuz topilmadi. Profilga aniqroq rasm yuklang."
            })

        similarity = _compare_faces(face_captured, face_saved)
        if similarity < FACE_MATCH_THRESHOLD:
            return JsonResponse({
                'success': False,
                'message': f"Yuz mos kelmadi (o'xshashlik: {similarity:.0%}). Qaytadan urinib ko'ring."
            })

        today = date.today()
        now = timezone.localtime().time()

        attendance, _ = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={'status': 'present', 'created_by': request.user}
        )

        # Muhim fix: agar yozuv bor, lekin check_in yo'q bo'lsa, uni "Kirish" deb belgilaydi.
        if not attendance.check_in:
            attendance.check_in = now
            attendance.status = 'present'
            action = "Kirish"
        elif not attendance.check_out:
            attendance.check_out = now
            action = "Chiqish"
        else:
            return JsonResponse({'success': False, 'message': "Bugungi davomat yakunlangan"})

        attendance.created_by = attendance.created_by or request.user
        attendance.notes = f"Face ID orqali tasdiqlandi. O'xshashlik: {similarity:.0%}"
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

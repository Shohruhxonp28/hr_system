# HRMS — Kadrlar va Ish Haqi Boshqaruvi Tizimi

O'zbek tilida HR/Admin paneli. Django + Bootstrap 5 + Chart.js + SQLite.

---

## 🚀 Ishga tushirish

### 1. Virtual muhit yarating
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 2. Django o'rnating
```bash
pip install -r requirements.txt
```

### 3. Ma'lumotlar bazasini yarating
```bash
python manage.py migrate
```

### 4. Namuna ma'lumotlarini yuklang
```bash
python manage.py seed_data
```

### 5. Serverni ishga tushiring
```bash
python manage.py runserver
```

### 6. Brauzerda oching
```
http://127.0.0.1:8000
```

---

## 🔐 Kirish ma'lumotlari
| Maydon | Qiymat |
|--------|--------|
| Login  | admin  |
| Parol  | admin123 |

---

## 📋 Sahifalar

| Sahifa | URL |
|--------|-----|
| Boshqaruv paneli | `/` |
| Xodimlar | `/employees/` |
| Bo'limlar | `/departments/` |
| Lavozimlar | `/positions/` |
| Ish jadvallari | `/schedules/` |
| Davomat | `/attendance/` |
| Ommaviy davomat | `/attendance/bulk/` |
| Ish haqi | `/payroll/` |
| Hisobotlar | `/reports/` |

---

## ⚙️ Texnik stek

- **Backend**: Django 4.2, SQLite
- **Frontend**: Bootstrap 5.3, Chart.js 4.4, Bootstrap Icons
- **Til**: O'zbek tili (UZ)
- **Vaqt zonasi**: Asia/Tashkent

---

## 💡 Asosiy funksiyalar

- ✅ Login / Logout
- ✅ Dashboard (6 ta statistik karta + grafiklar)
- ✅ Xodimlar CRUD (qidirish + filter)
- ✅ Bo'limlar CRUD
- ✅ Lavozimlar CRUD
- ✅ Ish jadvallari CRUD + haftalik ish kunlari
- ✅ Davomat qo'shish (yakka va ommaviy)
- ✅ Davomat filtrlash (sana, xodim, bo'lim, holat)
- ✅ Ish haqi hisoblash (kechikish, erta ketish, kelmagan kun, qo'shimcha ish)
- ✅ Ish haqi tafsiloti + to'landi belgisi
- ✅ Hisobotlar (donut chart, bar chart, trend)

---

## 📊 Davomat holatlari

| Holat | Tavsif |
|-------|--------|
| `present` | Vaqtida keldi |
| `late` | Kechikdi |
| `absent` | Kelmadi |
| `day_off` | Dam olish kuni |
| `holiday` | Bayram kuni |
| `incomplete` | To'liq emas |
| `overtime` | Qo'shimcha ish |

---

## 💰 Ish haqi hisoblash qoidalari

- **Kechikish**: Har 30 daqiqaga kunlik maoshning 0.5% ayiriladi
- **Erta ketish**: Ketgan vaqt soatlik stavka bo'yicha ayiriladi  
- **Kelmagan kun**: To'liq kunlik maosh ayiriladi
- **Qo'shimcha ish**: 1.5x soatlik stavka to'lanadi
- **Kunlik stavka**: Oylik maosh ÷ 26 ish kuni
- **Soatlik stavka**: Kunlik stavka ÷ 8 soat

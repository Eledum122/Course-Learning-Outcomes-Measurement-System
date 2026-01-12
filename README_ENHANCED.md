# نظام قياس مخرجات التعلم للمقررات الدراسية - النسخة المحسّنة
## Course Learning Outcomes Measurement System - Enhanced Version

---

## 📋 نظرة عامة | Overview

نظام شامل ومحسّن لقياس مخرجات التعلم للمقررات الدراسية يتبع معايير NCAAA (الهيئة الوطنية للتقويم والاعتماد الأكاديمي).

A comprehensive and enhanced system for measuring Course Learning Outcomes (CLOs) following NCAAA standards.

### ✨ التحسينات في هذه النسخة | Enhancements

1. **لوحة تحكم احترافية (Dashboard)**
   - عرض إحصائيات سريعة
   - الإجراءات السريعة
   - المقررات الأخيرة
   - التنبيهات والإشعارات

2. **واجهة مستخدم محسّنة**
   - أزرار عصرية مع تأثيرات بصرية
   - أيقونات رموزية واضحة
   - بطاقات معلومات منظمة
   - شارات حالة ملونة

3. **مكونات قابلة لإعادة الاستخدام**
   - EnhancedButton: أزرار محسّنة
   - CardFrame: إطارات بطاقات
   - InfoLabel: تسميات معلومات
   - StatusBadge: شارات حالة
   - SearchEntry: حقل بحث محسّن

4. **نظام أيقونات شامل**
   - أيقونات رموزية (Emoji Icons)
   - تصنيف منطقي للأيقونات
   - دوال مساعدة للوصول السهل

---

## 🎯 المراحل الثلاث | Three Stages

### المرحلة الأولى: بيانات المقرر (Stage 1: Course Data) ✅
**الحالة:** مكتملة ومحسّنة

**الصلاحيات:** مدير البرنامج

**المكونات:**
1. معلومات المقرر الأساسية
2. نواتج التعلم (CLOs)
3. موضوعات المقرر
4. أنشطة التقييم
5. جدول المواصفات

### المرحلة الثانية: بناء مراحل القياس (Stage 2: Measurement Framework) 🔄
**الحالة:** قيد التطوير

**الصلاحيات:** مدير البرنامج + منسق المقرر

**المكونات:**
- إعداد معايير القياس
- توزيع الدرجات
- ربط الأنشطة بالمخرجات

### المرحلة الثالثة: بيانات الطلاب (Stage 3: Students Data) ⏳
**الحالة:** مخطط لها

**الصلاحيات:** مدير البرنامج + منسق المقرر + أستاذ المقرر

**المكونات:**
- إدخال بيانات الطلاب
- تسجيل الدرجات
- حساب النتائج
- توليد التقارير

---

## 🚀 التشغيل السريع | Quick Start

### المتطلبات | Requirements

```bash
Python 3.7+
tkinter (مدمج مع Python)
```

### التثبيت | Installation

```bash
# 1. استخراج الملف المضغوط
unzip CLOs_Measurement_System_Enhanced.zip

# 2. الانتقال إلى المجلد
cd CLOs_Measurement_System_Enhanced

# 3. تشغيل البرنامج
python main.py
```

### بيانات تسجيل الدخول الافتراضية | Default Login

```
Username: admin
Password: admin123
```

---

## 📂 الهيكل التنظيمي | Directory Structure

```
CLOs_Measurement_System_Enhanced/
├── main.py                    # نقطة البداية
├── config.py                  # الإعدادات الأساسية
├── translations.py            # الترجمات (عربي/إنجليزي)
│
├── assets/                    # الأصول المحسّنة
│   ├── icons.py              # نظام الأيقونات
│   └── widgets.py            # المكونات المحسّنة
│
├── models/                    # نماذج البيانات
│   ├── course.py             # نموذج المقرر
│   └── user.py               # نموذج المستخدم
│
├── managers/                  # مدراء النظام
│   ├── access_control.py     # التحكم بالصلاحيات
│   └── course_manager.py     # إدارة المقررات
│
├── views/                     # واجهات المستخدم
│   ├── login_dialog.py       # شاشة تسجيل الدخول
│   ├── main_window.py        # النافذة الرئيسية المحسّنة
│   └── dashboard.py          # لوحة التحكم الجديدة
│
├── dialogs/                   # النوافذ الحوارية
│   ├── stage1_course_dialog.py    # المرحلة الأولى
│   └── open_course_dialog.py      # فتح مقرر
│
├── data/                      # البيانات
│   ├── users.json            # المستخدمون
│   ├── courses/              # المقررات
│   ├── reports/              # التقارير
│   ├── logs/                 # السجلات
│   └── backups/              # النسخ الاحتياطية
│
└── docs/                      # الوثائق
    ├── START_HERE.md
    ├── INSTALLATION_GUIDE.md
    └── ...
```

---

## 🎨 الألوان الرسمية | Official Colors

### جامعة تبوك | University of Tabuk

- **الأخضر الداكن:** `#2D5F3F`
- **الذهبي:** `#D4AF37`

### ألوان الحالة | Status Colors

- **مسودة (Draft):** `#95A5A6`
- **نشط (Active):** `#3498DB`
- **مكتمل (Completed):** `#2ECC71`
- **مغلق (Locked):** `#E67E22`
- **معتمد (Approved):** `#27AE60`

---

## 👥 الأدوار والصلاحيات | Roles & Permissions

### 1. مدير البرنامج (Program Manager) 👔
**الصلاحيات:**
- إنشاء مقررات جديدة
- تحديث بيانات المقررات
- حذف المقررات
- الموافقة على المقررات
- عرض جميع المقررات
- إدارة المستخدمين

### 2. منسق المقرر (Course Coordinator) 📊
**الصلاحيات:**
- إنشاء إطار القياس
- تحديث إطار القياس
- عرض بيانات المقرر الأساسية
- عرض جميع الشعب
- توليد تقارير موحدة

### 3. أستاذ المقرر (Course Instructor) 👨‍🏫
**الصلاحيات:**
- إنشاء شعبة جديدة
- إدخال بيانات الطلاب
- تسجيل الدرجات
- توليد تقارير الشعبة

### 4. مسؤول الجودة (Quality Officer) ✅
**الصلاحيات:**
- عرض جميع المقررات
- عرض جميع التقارير
- مراجعة البيانات

### 5. مدير النظام (Admin) ⚙
**الصلاحيات:**
- جميع الصلاحيات

---

## 📊 المميزات الجديدة | New Features

### 1. لوحة التحكم Dashboard

```python
# الإحصائيات السريعة
- إجمالي المقررات
- المقررات النشطة
- المقررات المكتملة
- التقارير

# الإجراءات السريعة
- إنشاء مقرر جديد
- فتح مقرر
- عرض التقارير
- الإعدادات

# المقررات الأخيرة
- جدول تفاعلي
- معلومات كاملة
- إجراءات سريعة
```

### 2. المكونات المحسّنة

```python
# EnhancedButton
btn = EnhancedButton(
    parent,
    text='حفظ',
    icon='save',
    command=save_function,
    style='primary'
)

# CardFrame
card = CardFrame(
    parent,
    title='معلومات المقرر',
    title_icon='course'
)

# InfoLabel
label = InfoLabel(
    parent,
    text='تم الحفظ بنجاح',
    icon_type='success'
)

# StatusBadge
badge = StatusBadge(
    parent,
    status='active'
)
```

---

## 🔧 التكوين | Configuration

### ملف config.py

```python
# تخصيص الألوان
COLORS = {
    'primary_green': '#2D5F3F',
    'primary_gold': '#D4AF37',
    # ...
}

# تخصيص الخطوط
FONTS = {
    'arabic_main': ('Arial', 12),
    'arabic_header': ('Arial', 16, 'bold'),
    # ...
}
```

---

## 📖 الوثائق | Documentation

للحصول على معلومات مفصلة، راجع:

- [البداية السريعة](docs/START_HERE.md)
- [دليل التثبيت](docs/INSTALLATION_GUIDE.md)
- [بنية التطبيق](docs/APPLICATION_STRUCTURE.md)
- [وثائق المرحلة الأولى](docs/STAGE1_DEVELOPMENT_DOCUMENTATION.md)

---

## 🤝 المساهمة | Contributing

نرحب بالمساهمات! يرجى:

1. Fork المشروع
2. إنشاء فرع جديد
3. إجراء التعديلات
4. إرسال Pull Request

---

## 📝 الترخيص | License

© 2024 University of Tabuk - Department of Statistics
جميع الحقوق محفوظة | All Rights Reserved

---

## 👤 المؤلف | Author

**د. حسين يوسف عبدالعظيم**
Dr. Hussein Youssef Abdelazim

الأستاذ بقسم الإحصاء - جامعة تبوك
Professor, Department of Statistics - University of Tabuk

---

## 📞 الدعم | Support

للدعم الفني أو الاستفسارات:

- Email: [email protected]
- الموقع: www.ut.edu.sa

---

## 🎉 شكر وتقدير | Acknowledgments

- جامعة تبوك - University of Tabuk
- كلية العلوم - Faculty of Science
- قسم الإحصاء - Department of Statistics
- الهيئة الوطنية للتقويم والاعتماد الأكاديمي - NCAAA

---

**الإصدار:** 2.0 (Enhanced)
**التاريخ:** December 2024

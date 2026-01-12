# دليل التثبيت والتحديث - المرحلة الأولى
# Installation & Update Guide - Stage 1

## 📋 جدول المحتويات

1. [الملفات الجديدة](#الملفات-الجديدة)
2. [الملفات المعدلة](#الملفات-المعدلة)
3. [خطوات التثبيت](#خطوات-التثبيت)
4. [مخطط التطبيق المحدث](#مخطط-التطبيق-المحدث)
5. [التحقق من التثبيت](#التحقق-من-التثبيت)

---

## 📁 الملفات الجديدة (New Files)

### 1. نماذج البيانات (Models)

#### ملف: `models/course.py`
```
المسار: CLOs_Measurement_System/models/course.py
الحالة: جديد ⭐
الحجم: 848 سطر
الوصف: نماذج بيانات المقرر الكاملة
```

**المحتويات:**
- `Semester` (Enum) - الفصول الدراسية
- `CLOCategory` (Enum) - فئات نواتج التعلم
- `CourseInfo` - معلومات المقرر الأساسية
- `CLO` - نواتج تعلم المقرر
- `Topic` - موضوعات المقرر
- `AssessmentActivity` - أنشطة التقييم
- `TableOfSpecifications` - جدول المواصفات
- `Course` - النموذج الرئيسي الشامل

**الإجراء:** انسخ الملف إلى `models/course.py`

---

### 2. المديرون (Managers)

#### ملف: `managers/course_manager.py`
```
المسار: CLOs_Measurement_System/managers/course_manager.py
الحالة: جديد ⭐
الحجم: 333 سطر
الوصف: مدير عمليات المقررات
```

**المحتويات:**
- إدارة دورة حياة المقرر (Create, Read, Update, Delete)
- عمليات البحث والاستعلام
- إدارة المكونات (CLOs, Topics, Activities)
- إدارة سير العمل (Workflow)
- الإحصائيات والتقارير

**الإجراء:** انسخ الملف إلى `managers/course_manager.py`

---

### 3. الواجهات (Dialogs)

#### ملف: `dialogs/stage1_course_dialog.py`
```
المسار: CLOs_Measurement_System/dialogs/stage1_course_dialog.py
الحالة: جديد ⭐
الحجم: 1,139 سطر
الوصف: واجهة إدارة بيانات المقرر - المرحلة الأولى
```

**المحتويات:**
- 5 تبويبات (معلومات، نواتج، موضوعات، أنشطة، مواصفات)
- نماذج إدخال شاملة
- قوائم عرض تفاعلية
- نظام التحقق والحفظ
- التكامل مع CourseManager

**الإجراء:** انسخ الملف إلى `dialogs/stage1_course_dialog.py`

---

## 🔄 الملفات المعدلة (Modified Files)

### 1. ملف: `models/__init__.py`

**الحالة:** محدّث 🔄

**المحتوى القديم:**
```python
"""
نماذج البيانات
Data Models
"""

from models.user import User

__all__ = ['User']
```

**المحتوى الجديد:**
```python
"""
نماذج البيانات
Data Models
"""

from models.user import User
from models.course import (
    Course, CourseInfo, CLO, Topic, AssessmentActivity,
    TableOfSpecifications, Semester, CLOCategory
)

__all__ = [
    'User',
    'Course',
    'CourseInfo',
    'CLO',
    'Topic',
    'AssessmentActivity',
    'TableOfSpecifications',
    'Semester',
    'CLOCategory'
]
```

**الإجراء:** استبدل محتوى الملف بالمحتوى الجديد
**المسار:** `CLOs_Measurement_System/models/__init__.py`

---

### 2. ملف: `managers/__init__.py`

**الحالة:** محدّث 🔄

**المحتوى القديم:**
```python
"""
مديرو النظام
System Managers
"""

from managers.access_control import AccessControl

__all__ = ['AccessControl']
```

**المحتوى الجديد:**
```python
"""
مديرو النظام
System Managers
"""

from managers.access_control import AccessControl
from managers.course_manager import CourseManager

__all__ = ['AccessControl', 'CourseManager']
```

**الإجراء:** استبدل محتوى الملف بالمحتوى الجديد
**المسار:** `CLOs_Measurement_System/managers/__init__.py`

---

### 3. ملف: `translations.py`

**الحالة:** محدّث 🔄 (إضافة مصطلحات جديدة)

**التعديلات:**
- إضافة 72 مصطلح جديد للمرحلة الأولى
- جميع المصطلحات المتعلقة بإدارة بيانات المقرر
- رسائل النظام والأخطاء
- نصوص المساعدة

**الإجراء:** استبدل الملف بالكامل أو أضف المصطلحات الجديدة في نهاية الملف
**المسار:** `CLOs_Measurement_System/translations.py`

**المصطلحات المضافة:**
```python
# المرحلة الأولى - بيانات المقرر
'stage1_course_data': {...},
'course_information': {...},
'course_title': {...},
'course_code': {...},
# ... إلخ (72 مصطلح)
```

---

## 📂 هيكل المجلدات المطلوب

تأكد من وجود المجلدات التالية:

```
CLOs_Measurement_System/
├── data/
│   ├── courses/          ⭐ جديد - يجب إنشاؤه
│   ├── reports/          (موجود)
│   ├── backups/          (موجود)
│   └── logs/             (موجود)
```

**الإجراء لإنشاء المجلد:**
```bash
mkdir -p CLOs_Measurement_System/data/courses
```

أو في Python:
```python
import os
os.makedirs('CLOs_Measurement_System/data/courses', exist_ok=True)
```

---

## 🔧 خطوات التثبيت التفصيلية

### الخطوة 1: نسخ الملفات الجديدة

```bash
# انتقل إلى مجلد المشروع
cd /path/to/CLOs_Measurement_System

# نسخ نماذج البيانات
cp /path/to/Stage1_Development/course.py models/

# نسخ المديرين
cp /path/to/Stage1_Development/course_manager.py managers/

# نسخ الواجهات
cp /path/to/Stage1_Development/stage1_course_dialog.py dialogs/
```

### الخطوة 2: تحديث الملفات الموجودة

```bash
# تحديث models/__init__.py
cp /path/to/Stage1_Development/models__init__.py models/__init__.py

# تحديث managers/__init__.py
cp /path/to/Stage1_Development/managers__init__.py managers/__init__.py

# تحديث translations.py
cp /path/to/Stage1_Development/translations.py translations.py
```

### الخطوة 3: إنشاء المجلدات المطلوبة

```bash
mkdir -p data/courses
```

### الخطوة 4: التحقق من الهيكل

```bash
# تحقق من وجود جميع الملفات
ls -l models/course.py
ls -l managers/course_manager.py
ls -l dialogs/stage1_course_dialog.py
ls -l data/courses/
```

---

## 🗺️ مخطط التطبيق المحدث

### البنية الكاملة للمشروع:

```
CLOs_Measurement_System/
│
├── 📄 main.py                          (موجود - نقطة البداية)
├── 📄 config.py                        (موجود - الإعدادات)
├── 📄 translations.py                  🔄 محدّث (72 مصطلح جديد)
│
├── 📁 models/                          (نماذج البيانات)
│   ├── 📄 __init__.py                  🔄 محدّث
│   ├── 📄 user.py                      (موجود)
│   └── 📄 course.py                    ⭐ جديد (8 فئات)
│
├── 📁 managers/                        (مديرو النظام)
│   ├── 📄 __init__.py                  🔄 محدّث
│   ├── 📄 access_control.py           (موجود)
│   └── 📄 course_manager.py            ⭐ جديد (25+ دالة)
│
├── 📁 views/                           (الواجهات الرئيسية)
│   ├── 📄 __init__.py                  (موجود)
│   ├── 📄 main_window.py               (موجود)
│   └── 📄 login_dialog.py              (موجود)
│
├── 📁 dialogs/                         (النوافذ الفرعية)
│   ├── 📄 __init__.py                  (موجود)
│   └── 📄 stage1_course_dialog.py      ⭐ جديد (5 تبويبات)
│
├── 📁 utils/                           (المساعدات)
│   └── 📄 __init__.py                  (موجود)
│
├── 📁 data/                            (البيانات)
│   ├── 📁 courses/                     ⭐ جديد (ملفات JSON للمقررات)
│   ├── 📁 reports/                     (موجود)
│   ├── 📁 backups/                     (موجود)
│   └── 📁 logs/                        (موجود)
│
├── 📄 README.md                        (موجود)
├── 📄 DEVELOPER_GUIDE.md               (موجود)
└── 📄 project_structure.txt            (موجود)
```

**الرموز:**
- ⭐ = ملف/مجلد جديد
- 🔄 = ملف محدّث
- (موجود) = ملف موجود من قبل بدون تعديل

---

## 🔗 العلاقات بين المكونات

```
┌─────────────────────────────────────────────────────────┐
│                      main.py                            │
│                   (نقطة البداية)                        │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                 views/main_window.py                     │
│                  (الواجهة الرئيسية)                     │
└────────────┬────────────────────────┬────────────────────┘
             │                        │
             ▼                        ▼
┌────────────────────┐    ┌──────────────────────────────┐
│ managers/          │    │ dialogs/                     │
│ access_control.py  │    │ stage1_course_dialog.py ⭐   │
│ (التحكم بالصلاحيات)│    │ (واجهة المرحلة الأولى)       │
└─────────┬──────────┘    └──────────┬───────────────────┘
          │                          │
          │                          ▼
          │              ┌──────────────────────────────┐
          │              │ managers/                    │
          │              │ course_manager.py ⭐         │
          │              │ (مدير المقررات)             │
          │              └──────────┬───────────────────┘
          │                         │
          │                         ▼
          │              ┌──────────────────────────────┐
          │              │ models/                      │
          │              │ course.py ⭐                 │
          │              │ (نماذج البيانات)            │
          │              └──────────┬───────────────────┘
          │                         │
          │                         ▼
          │              ┌──────────────────────────────┐
          │              │ data/courses/                │
          │              │ {course_id}.json ⭐          │
          │              │ (تخزين البيانات)            │
          │              └──────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│                    models/user.py                        │
│                  (نماذج المستخدمين)                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 التحقق من التثبيت

### اختبار سريع من Python Console:

```python
# اختبار 1: استيراد النماذج
from models.course import Course, CLO, CLOCategory
print("✓ نماذج المقرر تم استيرادها بنجاح")

# اختبار 2: استيراد المدير
from managers.course_manager import CourseManager
cm = CourseManager()
print("✓ مدير المقررات تم إنشاؤه بنجاح")

# اختبار 3: إنشاء مقرر تجريبي
course = cm.create_course('test_course', 'admin')
print(f"✓ تم إنشاء مقرر تجريبي: {course.course_id}")

# اختبار 4: حفظ وتحميل
cm.save_course(course)
loaded = cm.load_course('test_course')
print(f"✓ تم حفظ وتحميل المقرر بنجاح")

# اختبار 5: استيراد الواجهة
from dialogs.stage1_course_dialog import Stage1CourseDialog
print("✓ واجهة المرحلة الأولى تم استيرادها بنجاح")

print("\n✅ جميع الاختبارات نجحت! التثبيت صحيح.")
```

### اختبار شامل باستخدام ملف الاختبار:

```bash
# نسخ ملف الاختبار
cp /path/to/Stage1_Development/test_stage1.py .

# تشغيل الاختبارات
python test_stage1.py
```

**النتيجة المتوقعة:**
```
╔══════════════════════════════════════════════════════════╗
║          اختبار المرحلة الأولى - بيانات المقرر          ║
║          Stage 1 Testing - Course Data               ║
╚══════════════════════════════════════════════════════════╝

============================================================
اختبار إنشاء مقرر | Testing Course Creation
============================================================
✓ تم إنشاء المقرر: STAT401 - Applied Statistics...

... (المزيد من الاختبارات)

✅ اكتملت جميع الاختبارات بنجاح!
```

---

## 📊 جدول ملخص الملفات

| الملف | الحالة | المسار | الحجم | الإجراء |
|-------|--------|--------|-------|---------|
| `course.py` | ⭐ جديد | `models/` | 848 سطر | نسخ |
| `course_manager.py` | ⭐ جديد | `managers/` | 333 سطر | نسخ |
| `stage1_course_dialog.py` | ⭐ جديد | `dialogs/` | 1,139 سطر | نسخ |
| `models/__init__.py` | 🔄 محدّث | `models/` | - | استبدال |
| `managers/__init__.py` | 🔄 محدّث | `managers/` | - | استبدال |
| `translations.py` | 🔄 محدّث | `.` | +72 مصطلح | استبدال |
| `data/courses/` | ⭐ جديد | `data/` | مجلد | إنشاء |

**المجموع:**
- **3 ملفات جديدة** للنسخ
- **3 ملفات محدثة** للاستبدال
- **1 مجلد جديد** للإنشاء

---

## ⚠️ ملاحظات مهمة

### 1. النسخ الاحتياطي
**قبل التثبيت، قم بعمل نسخة احتياطية:**
```bash
cp -r CLOs_Measurement_System CLOs_Measurement_System_backup_$(date +%Y%m%d)
```

### 2. المتطلبات
- Python 3.8 أو أحدث
- Tkinter (مثبت مع Python عادةً)
- لا توجد مكتبات خارجية إضافية

### 3. الترميز
- جميع الملفات بترميز UTF-8
- تدعم العربية والإنجليزية بشكل كامل

### 4. الصلاحيات
تأكد من أن مجلد `data/courses` له صلاحيات الكتابة:
```bash
chmod -R 755 data/courses
```

---

## 🚀 الاستخدام بعد التثبيت

### من الكود الرئيسي:

```python
from dialogs.stage1_course_dialog import Stage1CourseDialog
from managers.course_manager import CourseManager

# في الواجهة الرئيسية، أضف زر أو قائمة:
def open_course_management(self):
    """فتح واجهة إدارة المقررات"""
    course_manager = CourseManager()
    
    dialog = Stage1CourseDialog(
        parent=self,
        course_manager=course_manager,
        current_user=self.current_user,
        course_id=None,  # None لمقرر جديد
        language=self.current_language
    )
```

### لفتح مقرر موجود:

```python
def open_existing_course(self, course_id):
    """فتح مقرر موجود للتعديل"""
    course_manager = CourseManager()
    
    dialog = Stage1CourseDialog(
        parent=self,
        course_manager=course_manager,
        current_user=self.current_user,
        course_id=course_id,  # معرف المقرر
        language=self.current_language
    )
```

---

## 📞 الدعم والمساعدة

إذا واجهت أي مشاكل:

1. **تحقق من الأخطاء:** راجع رسائل الأخطاء في Console
2. **اختبر الواردات:** استخدم الاختبار السريع أعلاه
3. **راجع التوثيق:** STAGE1_DEVELOPMENT_DOCUMENTATION.md
4. **شغّل الاختبارات:** `python test_stage1.py`

---

## ✅ قائمة التحقق النهائية

قبل البدء في استخدام النظام، تأكد من:

- [ ] نسخ الملفات الثلاثة الجديدة إلى المسارات الصحيحة
- [ ] تحديث الملفات الثلاثة المعدلة
- [ ] إنشاء مجلد `data/courses`
- [ ] تشغيل الاختبار السريع بنجاح
- [ ] عمل نسخة احتياطية من النظام القديم
- [ ] التأكد من صلاحيات المجلدات

---

**تم التحديث:** 23 ديسمبر 2024
**الإصدار:** Stage 1 - v1.0
**الحالة:** جاهز للتثبيت ✓

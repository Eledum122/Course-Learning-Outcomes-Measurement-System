# قائمة الملفات السريعة - Quick Files Checklist

## 📦 الملفات الجديدة للنسخ (3 ملفات)

### 1. course.py
```
المصدر: Stage1_Development/course.py
الوجهة: CLOs_Measurement_System/models/course.py
الحجم: 848 سطر
الوصف: نماذج بيانات المقرر (8 فئات)
```

**الأمر:**
```bash
cp Stage1_Development/course.py CLOs_Measurement_System/models/
```

---

### 2. course_manager.py
```
المصدر: Stage1_Development/course_manager.py
الوجهة: CLOs_Measurement_System/managers/course_manager.py
الحجم: 333 سطر
الوصف: مدير عمليات المقررات (25+ دالة)
```

**الأمر:**
```bash
cp Stage1_Development/course_manager.py CLOs_Measurement_System/managers/
```

---

### 3. stage1_course_dialog.py
```
المصدر: Stage1_Development/stage1_course_dialog.py
الوجهة: CLOs_Measurement_System/dialogs/stage1_course_dialog.py
الحجم: 1,139 سطر
الوصف: واجهة المرحلة الأولى (5 تبويبات)
```

**الأمر:**
```bash
cp Stage1_Development/stage1_course_dialog.py CLOs_Measurement_System/dialogs/
```

---

## 🔄 الملفات المحدثة للاستبدال (3 ملفات)

### 4. models/__init__.py
```
المصدر: Stage1_Development/models__init__.py
الوجهة: CLOs_Measurement_System/models/__init__.py
التعديل: إضافة تصدير نماذج المقرر
```

**الأمر:**
```bash
cp Stage1_Development/models__init__.py CLOs_Measurement_System/models/__init__.py
```

**أو استبدل المحتوى بـ:**
```python
from models.user import User
from models.course import (
    Course, CourseInfo, CLO, Topic, AssessmentActivity,
    TableOfSpecifications, Semester, CLOCategory
)

__all__ = [
    'User', 'Course', 'CourseInfo', 'CLO', 'Topic',
    'AssessmentActivity', 'TableOfSpecifications',
    'Semester', 'CLOCategory'
]
```

---

### 5. managers/__init__.py
```
المصدر: Stage1_Development/managers__init__.py
الوجهة: CLOs_Measurement_System/managers/__init__.py
التعديل: إضافة تصدير CourseManager
```

**الأمر:**
```bash
cp Stage1_Development/managers__init__.py CLOs_Measurement_System/managers/__init__.py
```

**أو استبدل المحتوى بـ:**
```python
from managers.access_control import AccessControl
from managers.course_manager import CourseManager

__all__ = ['AccessControl', 'CourseManager']
```

---

### 6. translations.py
```
المصدر: Stage1_Development/translations.py
الوجهة: CLOs_Measurement_System/translations.py
التعديل: إضافة 72 مصطلح جديد
```

**الأمر:**
```bash
cp Stage1_Development/translations.py CLOs_Measurement_System/
```

**ملاحظة:** هذا الملف كبير، يفضل الاستبدال الكامل

---

## 📁 المجلد الجديد للإنشاء

### 7. data/courses/
```
المسار: CLOs_Measurement_System/data/courses/
الوصف: مجلد تخزين ملفات المقررات بصيغة JSON
```

**الأمر:**
```bash
mkdir -p CLOs_Measurement_System/data/courses
```

**أو في Python:**
```python
import os
os.makedirs('CLOs_Measurement_System/data/courses', exist_ok=True)
```

---

## ⚡ التثبيت السريع (كل الأوامر مرة واحدة)

### نسخ لصقة واحدة - Linux/Mac:
```bash
#!/bin/bash

# المسارات
SOURCE_DIR="Stage1_Development"
TARGET_DIR="CLOs_Measurement_System"

# نسخ الملفات الجديدة
cp "$SOURCE_DIR/course.py" "$TARGET_DIR/models/"
cp "$SOURCE_DIR/course_manager.py" "$TARGET_DIR/managers/"
cp "$SOURCE_DIR/stage1_course_dialog.py" "$TARGET_DIR/dialogs/"

# نسخ الملفات المحدثة
cp "$SOURCE_DIR/models__init__.py" "$TARGET_DIR/models/__init__.py"
cp "$SOURCE_DIR/managers__init__.py" "$TARGET_DIR/managers/__init__.py"
cp "$SOURCE_DIR/translations.py" "$TARGET_DIR/"

# إنشاء المجلد
mkdir -p "$TARGET_DIR/data/courses"

echo "✅ تم التثبيت بنجاح!"
```

### Windows (PowerShell):
```powershell
# المسارات
$SOURCE_DIR = "Stage1_Development"
$TARGET_DIR = "CLOs_Measurement_System"

# نسخ الملفات الجديدة
Copy-Item "$SOURCE_DIR\course.py" "$TARGET_DIR\models\"
Copy-Item "$SOURCE_DIR\course_manager.py" "$TARGET_DIR\managers\"
Copy-Item "$SOURCE_DIR\stage1_course_dialog.py" "$TARGET_DIR\dialogs\"

# نسخ الملفات المحدثة
Copy-Item "$SOURCE_DIR\models__init__.py" "$TARGET_DIR\models\__init__.py"
Copy-Item "$SOURCE_DIR\managers__init__.py" "$TARGET_DIR\managers\__init__.py"
Copy-Item "$SOURCE_DIR\translations.py" "$TARGET_DIR\"

# إنشاء المجلد
New-Item -ItemType Directory -Force -Path "$TARGET_DIR\data\courses"

Write-Host "✅ تم التثبيت بنجاح!"
```

### Python Script:
```python
import shutil
import os

SOURCE_DIR = "Stage1_Development"
TARGET_DIR = "CLOs_Measurement_System"

# نسخ الملفات الجديدة
shutil.copy(f"{SOURCE_DIR}/course.py", f"{TARGET_DIR}/models/")
shutil.copy(f"{SOURCE_DIR}/course_manager.py", f"{TARGET_DIR}/managers/")
shutil.copy(f"{SOURCE_DIR}/stage1_course_dialog.py", f"{TARGET_DIR}/dialogs/")

# نسخ الملفات المحدثة
shutil.copy(f"{SOURCE_DIR}/models__init__.py", f"{TARGET_DIR}/models/__init__.py")
shutil.copy(f"{SOURCE_DIR}/managers__init__.py", f"{TARGET_DIR}/managers/__init__.py")
shutil.copy(f"{SOURCE_DIR}/translations.py", f"{TARGET_DIR}/")

# إنشاء المجلد
os.makedirs(f"{TARGET_DIR}/data/courses", exist_ok=True)

print("✅ تم التثبيت بنجاح!")
```

---

## ✅ قائمة التحقق بعد التثبيت

```
[ ] 1. تم نسخ course.py إلى models/
[ ] 2. تم نسخ course_manager.py إلى managers/
[ ] 3. تم نسخ stage1_course_dialog.py إلى dialogs/
[ ] 4. تم تحديث models/__init__.py
[ ] 5. تم تحديث managers/__init__.py
[ ] 6. تم تحديث translations.py
[ ] 7. تم إنشاء مجلد data/courses/

[ ] 8. تم اختبار الاستيراد:
    python -c "from models.course import Course; print('✓')"
    python -c "from managers.course_manager import CourseManager; print('✓')"
    python -c "from dialogs.stage1_course_dialog import Stage1CourseDialog; print('✓')"

[ ] 9. تم تشغيل ملف الاختبار:
    python test_stage1.py
```

---

## 📊 ملخص العمليات

| # | العملية | العدد | الحالة |
|---|---------|-------|--------|
| 1 | ملفات للنسخ | 3 | ⭐ جديد |
| 2 | ملفات للاستبدال | 3 | 🔄 محدّث |
| 3 | مجلدات للإنشاء | 1 | ⭐ جديد |
| **المجموع** | **7 عمليات** | | |

---

## 🎯 النتيجة النهائية

بعد تنفيذ جميع العمليات، يجب أن تكون البنية:

```
CLOs_Measurement_System/
├── models/
│   ├── __init__.py ✓
│   ├── user.py
│   └── course.py ⭐
├── managers/
│   ├── __init__.py ✓
│   ├── access_control.py
│   └── course_manager.py ⭐
├── dialogs/
│   ├── __init__.py
│   └── stage1_course_dialog.py ⭐
├── data/
│   └── courses/ ⭐
└── translations.py ✓
```

---

**تم:** 23 ديسمبر 2024
**الحالة:** جاهز للتثبيت ✓

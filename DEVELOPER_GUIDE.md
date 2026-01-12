# دليل المطور - نظام قياس مخرجات التعلم
# Developer Guide - CLOs Measurement System

## 📋 نظرة عامة على البناء

تم بناء النظام بشكل منظم ومقسم إلى ملفات متعددة لسهولة الصيانة والتطوير.

## 🏗️ البنية المعمارية

### 1. النمط المعماري: MVC (Model-View-Controller)

```
Models (النماذج)
  ↓
Managers (المديرون - Controllers)
  ↓
Views (الواجهات)
```

### 2. المكونات الأساسية

#### أ. الإعدادات (Configuration)
- `config.py`: جميع الإعدادات والثوابت
  - ألوان جامعة تبوك
  - الخطوط
  - المسارات
  - الأدوار والصلاحيات
  - إعدادات النافذة

#### ب. الترجمة (Translation)
- `translations.py`: نظام الترجمة الثنائي
  - قاموس شامل للترجمات
  - فئة `Translator` لإدارة اللغات
  - دوال مساعدة: `t()`, `set_language()`, `get_language()`

#### ج. النماذج (Models)
- `models/user.py`: نموذج المستخدم
  - تشفير كلمة المرور
  - إدارة الأدوار
  - التحويل من/إلى JSON

#### د. المديرون (Managers)
- `managers/access_control.py`: نظام الصلاحيات
  - إدارة المستخدمين (CRUD)
  - المصادقة والتخويل
  - التحقق من الصلاحيات
  - إدارة تعيينات الشعب

#### هـ. الواجهات (Views)
- `views/login_dialog.py`: نافذة تسجيل الدخول
- `views/main_window.py`: النافذة الرئيسية

## 📦 الملفات المُنشأة والجاهزة

### ✅ ملفات كاملة وجاهزة:

1. **config.py** (380 سطر)
   - نظام ألوان كامل
   - إعدادات شاملة
   - تعريف جميع الأدوار والصلاحيات

2. **translations.py** (440 سطر)
   - 150+ ترجمة
   - نظام ترجمة ديناميكي
   - دعم كامل للعربية والإنجليزية

3. **models/user.py** (110 سطر)
   - نموذج المستخدم الكامل
   - تشفير كلمة المرور
   - إدارة الأدوار

4. **managers/access_control.py** (300 سطر)
   - نظام صلاحيات متقدم
   - إدارة كاملة للمستخدمين
   - مستخدم افتراضي (admin/admin123)

5. **views/login_dialog.py** (240 سطر)
   - واجهة تسجيل دخول احترافية
   - دعم ثنائي اللغة
   - تصميم بألوان الجامعة

6. **views/main_window.py** (560 سطر)
   - النافذة الرئيسية الكاملة
   - لوحة المراحل الثلاث
   - نظام القوائم
   - شريط الحالة

7. **main.py** (70 سطر)
   - نقطة البداية
   - معالجة الأخطاء

## 🔄 تدفق البيانات

```
main.py
  ↓
LoginDialog → access_control.authenticate()
  ↓
MainWindow(user, access_control)
  ↓
Check Permissions → access_control.has_permission()
  ↓
Open Stage View (based on permission)
```

## 🎨 نظام الألوان في config.py

```python
COLORS = {
    'primary_green': '#2D5F3F',      # اللون الأساسي
    'primary_gold': '#D4AF37',       # اللون الثانوي
    'stage1_color': '#3498DB',       # أزرق - المرحلة الأولى
    'stage2_color': '#E74C3C',       # أحمر - المرحلة الثانية
    'stage3_color': '#2ECC71',       # أخضر - المرحلة الثالثة
    # ... المزيد
}
```

## 🔐 نظام الصلاحيات

### كيفية التحقق من الصلاحيات:

```python
# في الواجهة
if self.access_control.has_permission(self.user.user_id, 'create_course_master'):
    # عرض الزر أو الوظيفة
    pass
```

### الأدوار المعرفة في config.py:

```python
ROLES = {
    'program_manager': {...},
    'course_coordinator': {...},
    'course_instructor': {...},
    'department_head': {...},
    'admin': {...}
}
```

## 🌐 نظام الترجمة

### كيفية إضافة ترجمة جديدة:

1. افتح `translations.py`
2. أضف في قاموس `TRANSLATIONS`:

```python
'new_key': {
    'ar': 'النص بالعربي',
    'en': 'English Text'
}
```

3. استخدم في الكود:

```python
from translations import t

label_text = t('new_key')
```

### تغيير اللغة:

```python
from translations import set_language

set_language('ar')  # العربية
set_language('en')  # الإنجليزية
```

## 📁 إنشاء ملفات جديدة

### مثال: إنشاء نموذج Course

```python
# models/course.py

class Course:
    def __init__(self, course_id, course_code, title):
        self.course_id = course_id
        self.course_code = course_code
        self.title = title
        self.stage1_data = None
        self.stage2_data = None
        self.stage3_data = []
    
    def to_dict(self):
        return {
            'course_id': self.course_id,
            'course_code': self.course_code,
            'title': self.title,
            'stage1_data': self.stage1_data,
            'stage2_data': self.stage2_data,
            'stage3_data': self.stage3_data
        }
    
    @classmethod
    def from_dict(cls, data):
        course = cls(
            data['course_id'],
            data['course_code'],
            data['title']
        )
        course.stage1_data = data.get('stage1_data')
        course.stage2_data = data.get('stage2_data')
        course.stage3_data = data.get('stage3_data', [])
        return course
```

### مثال: إنشاء مدير Stage Manager

```python
# managers/stage_manager.py

import json
import os
from config import COURSES_DIR

class StageManager:
    def __init__(self, access_control):
        self.access_control = access_control
        self.current_course = None
    
    def create_stage1(self, user_id, course_data):
        # التحقق من الصلاحية
        if not self.access_control.has_permission(user_id, 'create_course_master'):
            raise PermissionError("No permission")
        
        # إنشاء البيانات
        stage1_data = {
            'metadata': {
                'created_by': user_id,
                'created_date': datetime.now().isoformat()
            },
            'course_data': course_data
        }
        
        # حفظ
        self.save_stage1(stage1_data)
        return stage1_data
```

### مثال: إنشاء واجهة Stage1

```python
# views/stage1_view.py

import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS
from translations import t

class Stage1View:
    def __init__(self, parent, user, access_control):
        self.frame = ttk.Frame(parent)
        self.user = user
        self.access_control = access_control
        
        self.create_widgets()
    
    def create_widgets(self):
        # عنوان
        title = tk.Label(
            self.frame,
            text=t('stage_1'),
            font=FONTS['arabic_header'],
            fg=COLORS['stage1_color']
        )
        title.pack(pady=10)
        
        # حقول الإدخال
        # ...
    
    def save_data(self):
        # حفظ البيانات
        pass
```

## 🧪 اختبار المكونات

### اختبار نموذج المستخدم:

```python
from models.user import User

# إنشاء مستخدم
user = User(
    user_id='test_001',
    username='test',
    password_hash=User.hash_password('password123'),
    full_name='Test User',
    roles=['admin']
)

# التحقق من كلمة المرور
assert user.verify_password('password123')

# إضافة دور
user.add_role('course_coordinator')
assert user.has_role('course_coordinator')
```

### اختبار نظام الصلاحيات:

```python
from managers.access_control import AccessControl

# إنشاء نظام الصلاحيات
ac = AccessControl()

# المصادقة
user = ac.authenticate('admin', 'admin123')
assert user is not None

# التحقق من الصلاحية
assert ac.has_permission(user.user_id, 'create_course_master')
```

## 📊 حفظ واسترجاع البيانات

### نمط JSON المستخدم:

```python
import json

# حفظ
data = {
    'course_id': 'STAT_324',
    'title': 'Applied Statistics',
    'stage1_data': {...}
}

with open('course.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# استرجاع
with open('course.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

## 🔨 الخطوات التالية للتطوير

### 1. إكمال النماذج (Models)
- [ ] `models/course.py`
- [ ] `models/stage1_data.py`
- [ ] `models/stage2_data.py`
- [ ] `models/stage3_data.py`

### 2. إكمال المديرين (Managers)
- [ ] `managers/stage_manager.py`
- [ ] `managers/data_manager.py`

### 3. إكمال الواجهات (Views)
- [ ] `views/stage1_view.py`
- [ ] `views/stage2_view.py`
- [ ] `views/stage3_view.py`

### 4. إنشاء الحوارات (Dialogs)
- [ ] `dialogs/user_management.py`
- [ ] `dialogs/course_selection.py`

### 5. إنشاء الأدوات المساعدة (Utils)
- [ ] `utils/validators.py`
- [ ] `utils/helpers.py`

## 💡 نصائح للتطوير

### 1. استخدم الإعدادات من config.py
```python
from config import COLORS, FONTS
button = tk.Button(bg=COLORS['btn_primary'], font=FONTS['arabic_main'])
```

### 2. استخدم الترجمات دائماً
```python
from translations import t
label = tk.Label(text=t('course_code'))
```

### 3. تحقق من الصلاحيات
```python
if not self.access_control.has_permission(user_id, 'permission_name'):
    messagebox.showerror(t('error'), t('permission_denied'))
    return
```

### 4. اتبع نمط التسمية
- الملفات: `snake_case.py`
- الفئات: `PascalCase`
- الدوال: `snake_case()`
- الثوابت: `UPPER_CASE`

### 5. استخدم Type Hints
```python
def create_user(name: str, email: str) -> User:
    pass
```

## 🐛 معالجة الأخطاء

```python
try:
    # العملية
    result = perform_operation()
except PermissionError:
    messagebox.showerror(t('error'), t('permission_denied'))
except ValueError as e:
    messagebox.showerror(t('error'), str(e))
except Exception as e:
    messagebox.showerror(t('error'), f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
```

## 📚 مراجع مفيدة

- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [Python JSON](https://docs.python.org/3/library/json.html)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

تم إعداد هذا الدليل بواسطة: د. حسين يوسف عبدالعظيم  
Prepared by: Dr. Hussein Youssef Abdelazim

قسم الإحصاء - جامعة تبوك  
Department of Statistics - University of Tabuk

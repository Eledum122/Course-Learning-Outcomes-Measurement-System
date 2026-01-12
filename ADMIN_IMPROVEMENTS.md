# تحسينات واجهة مدير البرنامج (Admin) - دليل شامل
## Admin Interface Improvements - Comprehensive Guide

---

## 📋 نظرة عامة | Overview

تم تطوير واجهة إدارية متقدمة وشاملة لمدير البرنامج (Admin) تتضمن:

1. **إدارة المستخدمين الكاملة** - نظام متقدم لإدارة حسابات المستخدمين
2. **سجل التدقيق** - تتبع جميع العمليات الحساسة في النظام
3. **النسخ الاحتياطي التلقائي** - نسخ احتياطية تلقائية ويدوية للبيانات
4. **إدارة الجلسات** - انتهاء صلاحية تلقائي للجلسات غير النشطة

---

## 🆕 الملفات الجديدة | New Files

### 1. `utils/audit_logger.py`
**سجل التدقيق - Audit Logger**

#### الوظائف:
- تسجيل جميع العمليات الحساسة (تسجيل دخول، إنشاء/تعديل/حذف المستخدمين، إلخ)
- البحث والتصفية في السجلات
- إحصائيات شاملة
- حذف السجلات القديمة تلقائياً

#### الاستخدام:
```python
from utils.audit_logger import log_login, log_create_user, audit_logger

# تسجيل دخول
log_login(username="admin", user_id="admin_001", success=True)

# إنشاء مستخدم
log_create_user(
    admin_username="admin",
    admin_id="admin_001",
    new_username="teacher1",
    roles=["course_instructor"]
)

# الحصول على السجلات
logs = audit_logger.get_recent_logs(limit=50)
stats = audit_logger.get_statistics()
```

#### الدوال المساعدة:
- `log_login()` - تسجيل دخول
- `log_logout()` - تسجيل خروج
- `log_create_user()` - إنشاء مستخدم
- `log_update_user()` - تحديث مستخدم
- `log_delete_user()` - حذف مستخدم
- `log_create_course()` - إنشاء مقرر
- `log_delete_course()` - حذف مقرر
- `log_backup()` - نسخ احتياطي
- `log_restore()` - استعادة

---

### 2. `managers/backup_manager.py`
**مدير النسخ الاحتياطي - Backup Manager**

#### الوظائف:
- نسخ احتياطي تلقائي كل 24 ساعة (افتراضياً)
- نسخ احتياطي يدوي بوصف اختياري
- استعادة من النسخ الاحتياطية
- حذف النسخ القديمة تلقائياً (الاحتفاظ بآخر 30 نسخة)
- تصدير النسخ إلى موقع خارجي

#### الاستخدام:
```python
from managers.backup_manager import backup_manager

# إنشاء نسخة احتياطية يدوية
backup_path = backup_manager.create_backup(
    backup_type='manual',
    description='قبل التحديث الكبير'
)

# الحصول على قائمة النسخ
backups = backup_manager.get_backup_list()

# استعادة من نسخة
success = backup_manager.restore_backup('backups/backup_manual_20250107_143000.zip')

# إحصائيات
stats = backup_manager.get_statistics()
```

#### الإعدادات:
- `data_dir`: مجلد البيانات (افتراضياً: "data")
- `backup_dir`: مجلد النسخ (افتراضياً: "backups")
- `auto_backup_enabled`: تفعيل النسخ التلقائي (افتراضياً: True)
- `backup_interval_hours`: الفترة بين النسخ (افتراضياً: 24 ساعة)
- `max_backups`: الحد الأقصى للنسخ (افتراضياً: 30)

---

### 3. `dialogs/admin_user_management_dialog.py`
**واجهة إدارة المستخدمين - User Management Dialog**

#### المميزات:
- **جدول شامل** لعرض جميع المستخدمين مع:
  - اسم المستخدم
  - الاسم الكامل
  - البريد الإلكتروني
  - الأدوار
  - الحالة (نشط/معطل)
  - آخر دخول

- **بحث متقدم** في جميع الحقول
- **إضافة مستخدم جديد** مع:
  - البيانات الأساسية
  - اختيار الأدوار (متعدد)
  - تفعيل/تعطيل الحساب

- **تعديل المستخدمين** الموجودين
- **حذف المستخدمين** (مع حماية من حذف المستخدم الحالي)
- **إحصائيات** شاملة
- **تصدير** قائمة المستخدمين إلى CSV

#### الاستخدام:
```python
from dialogs.admin_user_management_dialog import AdminUserManagementDialog

dialog = AdminUserManagementDialog(
    parent=root,
    access_control=access_control,
    language='ar'  # or 'en'
)
```

---

### 4. تحديثات على `managers/access_control.py`
**إدارة الجلسات - Session Management**

#### المميزات الجديدة:
- **انتهاء صلاحية الجلسات** تلقائياً بعد 120 دقيقة من عدم النشاط
- **تتبع النشاط** - يتم تحديث وقت آخر نشاط مع كل عملية
- **معلومات الجلسة** - معرفة الوقت المتبقي للجلسة
- **التكامل مع سجل التدقيق** - تسجيل تلقائي للدخول والخروج

#### الدوال الجديدة:
```python
# بدء جلسة
access_control.start_session(user)

# إنهاء جلسة
access_control.end_session()

# تحديث النشاط
access_control.update_activity()

# التحقق من انتهاء الصلاحية
if access_control.is_session_expired():
    # الجلسة منتهية

# معلومات الجلسة
session_info = access_control.get_session_info()
# {
#     'user_id': '...',
#     'username': '...',
#     'session_start': '...',
#     'last_activity': '...',
#     'time_remaining_minutes': 85,
#     'is_expired': False
# }

# التحقق والتحديث
if access_control.check_session_and_refresh():
    # الجلسة صالحة ومحدثة
else:
    # الجلسة منتهية - تم تسجيل الخروج تلقائياً
```

#### الإعدادات:
```python
# تغيير مدة انتهاء الجلسة (بالدقائق)
access_control = AccessControl(session_timeout_minutes=60)  # ساعة واحدة
```

---

## 📁 قائمة الإدارة الجديدة | New Admin Menu

تم إضافة قائمة **"الإدارة"** في شريط القوائم، تظهر **فقط للمستخدمين بدور Admin**.

### العناصر:
1. **إدارة المستخدمين** (Ctrl+U)
   - إضافة/تعديل/حذف المستخدمين
   - تعيين الأدوار
   - تفعيل/تعطيل الحسابات

2. **النسخ الاحتياطي** (Ctrl+B)
   - إنشاء نسخة احتياطية يدوية
   - استعادة من نسخة احتياطية

3. **سجل التدقيق** (Ctrl+Shift+A)
   - عرض آخر 100 عملية
   - تفاصيل كل عملية
   - حالة العملية (نجحت/فشلت/تحذير)

4. **إعدادات النظام**
   - إحصائيات النسخ الاحتياطي
   - إحصائيات سجل التدقيق
   - معلومات النظام

---

## ⌨️ اختصارات لوحة المفاتيح | Keyboard Shortcuts

### اختصارات Admin الجديدة:
- `Ctrl+U` - إدارة المستخدمين
- `Ctrl+B` - النسخ الاحتياطي والاستعادة
- `Ctrl+Shift+A` - سجل التدقيق

### اختصارات موجودة:
- `Ctrl+H` - الصفحة الرئيسية
- `Ctrl+N` - مقرر جديد
- `Ctrl+O` - فتح مقرر
- `Ctrl+R` - تقرير المقرر
- `Ctrl+L` - تغيير اللغة
- `Alt+F4` - إغلاق البرنامج

---

## 👥 الأدوار والصلاحيات | Roles & Permissions

### الأدوار المتاحة:

#### 1. **Admin** (مدير النظام)
- جميع الصلاحيات
- إدارة المستخدمين
- النسخ الاحتياطي والاستعادة
- الوصول إلى سجل التدقيق
- إعدادات النظام

#### 2. **Program Manager** (منسق البرنامج)
- إدارة جميع المقررات
- إنشاء/تعديل/حذف المقررات
- تعيين منسقي المقررات
- عرض تقارير شاملة

#### 3. **Course Coordinator** (منسق المقرر)
- إدارة مقرر محدد
- إنشاء إطار القياس (المرحلة 1 و 2)
- تعيين مدرسي الشعب
- عرض جميع شعب المقرر

#### 4. **Course Instructor** (مدرس الشعبة)
- إدارة شعبة محددة
- إدخال بيانات الطلاب
- إدخال الدرجات
- عرض تقارير شعبته فقط

#### 5. **Department Head** (رئيس القسم)
- عرض جميع المقررات
- عرض التقارير الشاملة
- لا يمكن التعديل

---

## 📊 سجل التدقيق | Audit Log

### العمليات المسجلة:

| العملية | الوصف |
|---------|-------|
| `login` | تسجيل دخول (ناجح/فاشل) |
| `logout` | تسجيل خروج |
| `create_user` | إنشاء مستخدم جديد |
| `update_user` | تحديث بيانات مستخدم |
| `delete_user` | حذف مستخدم |
| `create_course` | إنشاء مقرر |
| `delete_course` | حذف مقرر |
| `backup` | إنشاء نسخة احتياطية |
| `restore` | استعادة من نسخة |

### تفاصيل السجل:
```json
{
  "timestamp": "2025-01-07T14:30:45.123456",
  "action": "create_user",
  "user_id": "admin_001",
  "username": "admin",
  "status": "success",
  "details": {
    "new_username": "teacher1",
    "roles": ["course_instructor"]
  },
  "ip_address": null
}
```

### الاستعلام عن السجلات:
```python
# آخر 50 سجل
logs = audit_logger.get_recent_logs(limit=50)

# سجلات مستخدم محدد
logs = audit_logger.get_user_activity(user_id='admin_001', limit=50)

# محاولات تسجيل الدخول الفاشلة
failed_logins = audit_logger.get_failed_logins(limit=20)

# بحث متقدم
logs = audit_logger.get_logs(
    action='create_user',
    user_id='admin_001',
    status='success',
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 7),
    limit=100
)
```

---

## 💾 النسخ الاحتياطي | Backups

### أنواع النسخ:

#### 1. **النسخ التلقائية** (Auto Backups)
- تعمل كل 24 ساعة افتراضياً
- تعمل في الخلفية
- لا تحتاج تدخل المستخدم

#### 2. **النسخ اليدوية** (Manual Backups)
- يطلبها المستخدم
- يمكن إضافة وصف
- مفيدة قبل التحديثات الكبيرة

#### 3. **نسخ ما قبل الاستعادة** (Pre-restore Backups)
- تُنشأ تلقائياً قبل استعادة أي نسخة
- للأمان - في حالة فشل الاستعادة

### بنية ملف النسخة:
```
backup_manual_20250107_143000.zip
│
├── data/
│   ├── users.json
│   ├── courses/
│   ├── sections/
│   └── ...
│
└── backup_info.json
```

### معلومات النسخة:
```json
{
  "timestamp": "2025-01-07T14:30:00",
  "type": "manual",
  "description": "قبل التحديث الكبير",
  "files_count": 125
}
```

---

## 🔧 التكامل مع الكود الموجود | Integration

### في تسجيل الدخول:
```python
# في login_dialog.py أو main.py
if user:
    # بدء الجلسة
    access_control.start_session(user)

    # تسجيل في السجل (تلقائي داخل start_session)
    # log_login تُستدعى تلقائياً
```

### في تسجيل الخروج:
```python
# في main_window.py -> logout()
def logout(self):
    # إنهاء الجلسة
    self.access_control.end_session()

    # تسجيل الخروج (تلقائي داخل end_session)
    # log_logout تُستدعى تلقائياً

    # إغلاق النافذة
    self.root.destroy()
```

### في كل عملية مهمة:
```python
# تحديث النشاط
self.access_control.update_activity()

# التحقق من صلاحية الجلسة
if not self.access_control.check_session_and_refresh():
    # الجلسة منتهية
    messagebox.showwarning("تنبيه", "انتهت صلاحية جلستك. الرجاء تسجيل الدخول مرة أخرى.")
    self.logout()
    return
```

---

## 📝 أمثلة عملية | Practical Examples

### مثال 1: إضافة مستخدم جديد
```python
# في واجهة إدارة المستخدمين
user_id = access_control.create_user(
    username='teacher1',
    password='SecurePass123!',
    full_name='د. أحمد محمد',
    email='ahmad@tabuk.edu.sa',
    roles=['course_instructor'],
    phone='0501234567',
    department='قسم الإحصاء'
)

# التسجيل تلقائي في سجل التدقيق
# log_create_user يُستدعى داخل الواجهة
```

### مثال 2: إنشاء نسخة احتياطية قبل عملية حساسة
```python
# قبل حذف مقرر أو تحديث كبير
backup_path = backup_manager.create_backup(
    backup_type='manual',
    description='قبل حذف مقرر STAT101'
)

if backup_path:
    # المتابعة بالعملية الحساسة
    delete_course(course_id)

    # تسجيل العملية
    log_delete_course(
        username=current_user.username,
        user_id=current_user.user_id,
        course_name='STAT101',
        course_code='STAT101'
    )
```

### مثال 3: عرض نشاط مستخدم معين
```python
# في لوحة Admin
user_activity = audit_logger.get_user_activity(
    user_id='teacher1_001',
    limit=50
)

for log in user_activity:
    print(f"{log['timestamp']}: {log['action']} - {log['status']}")
```

---

## ⚠️ ملاحظات مهمة | Important Notes

### 1. الأمان:
- **كلمات المرور**: مشفرة باستخدام SHA-256
- **الجلسات**: تنتهي تلقائياً بعد 120 دقيقة من عدم النشاط
- **سجل التدقيق**: غير قابل للتعديل من الواجهة
- **النسخ الاحتياطي**: نسخة أمان تلقائية قبل أي استعادة

### 2. الأداء:
- **النسخ التلقائي**: يعمل في خيط منفصل (background thread)
- **سجل التدقيق**: ملف منفصل لكل شهر
- **حذف تلقائي**: للسجلات القديمة (90 يوماً) والنسخ القديمة (30 نسخة)

### 3. الصيانة:
- **مجلد السجلات**: `data/logs/`
- **مجلد النسخ**: `backups/`
- **التنظيف التلقائي**: يحدث عند كل عملية جديدة

### 4. المسارات:
```
CLOs_Measurement_System_03/
├── data/
│   ├── users.json
│   └── logs/
│       └── audit_202501.json
│
├── backups/
│   ├── backup_auto_20250107_000000.zip
│   ├── backup_manual_20250107_143000.zip
│   └── backup_config.json
│
├── utils/
│   └── audit_logger.py
│
├── managers/
│   ├── access_control.py (محدث)
│   └── backup_manager.py
│
└── dialogs/
    └── admin_user_management_dialog.py
```

---

## 🚀 البدء السريع | Quick Start

### 1. تشغيل البرنامج كـ Admin:
```bash
python main.py
```
- تسجيل الدخول: `admin` / `admin123`
- الانتقال إلى قائمة **الإدارة** 🛡️

### 2. إضافة مستخدم جديد:
- **الإدارة** → **إدارة المستخدمين** (أو Ctrl+U)
- انقر **➕ مستخدم جديد**
- املأ البيانات واختر الأدوار
- **💾 حفظ**

### 3. إنشاء نسخة احتياطية:
- **الإدارة** → **النسخ الاحتياطي** (أو Ctrl+B)
- اختر **نعم** لإنشاء نسخة
- أدخل وصفاً (اختياري)
- **موافق**

### 4. عرض سجل التدقيق:
- **الإدارة** → **سجل التدقيق** (أو Ctrl+Shift+A)
- عرض آخر 100 عملية مع التفاصيل

### 5. الإحصائيات:
- **الإدارة** → **إعدادات النظام**
- عرض إحصائيات النسخ والسجلات

---

## 🎯 الخطوات التالية | Next Steps

### 1. تخصيص الأدوار:
قد ترغب في إضافة أدوار مخصصة أو تعديل الصلاحيات في `config.py`:
```python
ROLES = {
    'custom_role': {
        'name_ar': 'دور مخصص',
        'name_en': 'Custom Role',
        'permissions': ['view_courses', 'create_activities']
    }
}
```

### 2. إضافة تنبيهات:
يمكن إضافة تنبيهات للعمليات الحساسة:
```python
def show_security_warning(action, details):
    messagebox.showwarning(
        "تحذير أمني",
        f"تم {action}\n\nالتفاصيل: {details}"
    )
```

### 3. توسيع سجل التدقيق:
إضافة المزيد من العمليات للتسجيل:
```python
def log_grade_modification(teacher, student, course, old_grade, new_grade):
    audit_logger.log(
        action='modify_grade',
        user_id=teacher.user_id,
        username=teacher.username,
        details={
            'student': student.name,
            'course': course.code,
            'old_grade': old_grade,
            'new_grade': new_grade
        },
        status='success'
    )
```

---

## 📞 الدعم | Support

في حالة وجود أي استفسارات أو مشاكل:
1. راجع هذا الدليل
2. تحقق من سجل التدقيق للمشاكل
3. تحقق من النسخ الاحتياطية
4. اتصل بمطور النظام

---

## 📄 الترخيص | License

هذا النظام مطور لجامعة تبوك - كلية العلوم - قسم الإحصاء

---

**آخر تحديث:** 7 يناير 2025
**الإصدار:** 2.0
**المطور:** Claude Sonnet 4.5

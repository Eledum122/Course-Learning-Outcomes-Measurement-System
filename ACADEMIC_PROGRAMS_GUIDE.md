# دليل نظام البرامج الأكاديمية
# Academic Programs System Guide

---

## المحتويات - Contents

1. [نظرة عامة - Overview](#overview)
2. [الهيكل التنظيمي - Organization Structure](#structure)
3. [كيفية الاستخدام - How to Use](#usage)
4. [إدارة البرامج - Program Management](#management)
5. [الصلاحيات والأدوار - Permissions & Roles](#permissions)
6. [الربط مع المقررات - Course Integration](#courses)

---

## <a name="overview"></a>نظرة عامة - Overview

نظام البرامج الأكاديمية هو الأساس الذي يُبنى عليه كل النظام. يوفر:
- إدارة كاملة للبرامج الأكاديمية المختلفة
- ربط كل برنامج بمنسق محدد
- تنظيم هرمي: جامعة ← كلية ← قسم ← برنامج
- صلاحيات محددة لكل منسق برنامج

The Academic Programs System is the foundation upon which the entire system is built. It provides:
- Complete management of different academic programs
- Link each program to a specific coordinator
- Hierarchical organization: University → College → Department → Program
- Specific permissions for each program coordinator

---

## <a name="structure"></a>الهيكل التنظيمي - Organization Structure

### الهرمية الإدارية - Administrative Hierarchy

```
جامعة تبوك (University of Tabuk)
    │
    ├── كلية العلوم (College of Science)
    │   │
    │   ├── قسم الإحصاء (Department of Statistics)
    │   │   │
    │   │   ├── بكالوريوس الإحصاء (Bachelor of Statistics)
    │   │   │   └── المنسق: د. أحمد محمد
    │   │   │
    │   │   └── ماجستير الإحصاء (Master of Statistics)
    │   │       └── المنسق: د. فاطمة علي
    │   │
    │   └── قسم الرياضيات (Department of Mathematics)
    │       └── ...
    │
    └── كلية الحاسبات (College of Computing)
        └── ...
```

### معلومات البرنامج - Program Information

كل برنامج أكاديمي يحتوي على:

Each academic program contains:

1. **المعلومات الأساسية - Basic Information**
   - اسم الجامعة (عربي/إنجليزي) - University Name (AR/EN)
   - اسم الكلية (عربي/إنجليزي) - College Name (AR/EN)
   - اسم القسم (عربي/إنجليزي) - Department Name (AR/EN)
   - اسم البرنامج (عربي/إنجليزي) - Program Name (AR/EN)
   - رمز البرنامج (اختياري) - Program Code (optional)

2. **معلومات المنسق - Coordinator Information**
   - معرف المنسق (user_id) - Coordinator ID
   - الربط مع نظام المستخدمين - Integration with user system
   - يجب أن يكون للمنسق صلاحية `program_manager`

3. **معلومات إضافية - Additional Information**
   - الوصف (عربي/إنجليزي) - Description (AR/EN)
   - تاريخ الإنشاء - Creation Date
   - آخر تعديل - Last Modified
   - الحالة (نشط/معطل) - Status (Active/Inactive)

---

## <a name="usage"></a>كيفية الاستخدام - How to Use

### 1. الوصول إلى إدارة البرامج
### Accessing Programs Management

**للمدير (Admin) فقط:**

1. شغّل البرنامج - Run the application
2. سجل دخول كمدير - Login as admin
3. اختر قائمة **"الإدارة"** - Select **"Admin"** menu
4. اختر **"إدارة البرامج الأكاديمية"** - Select **"Academic Programs"**

أو استخدم الاختصار: `Ctrl+P`

Or use shortcut: `Ctrl+P`

---

### 2. إضافة برنامج جديد
### Adding a New Program

**الخطوات - Steps:**

1. اضغط على **"➕ برنامج جديد"** - Click **"➕ New Program"**

2. املأ المعلومات المطلوبة - Fill required information:

   **مطلوب - Required:**
   - اسم البرنامج (عربي) - Program Name (Arabic)
   - اسم البرنامج (إنجليزي) - Program Name (English)
   - منسق البرنامج - Program Coordinator

   **اختياري - Optional:**
   - الجامعة (افتراضي: جامعة تبوك) - University (default: University of Tabuk)
   - الكلية - College
   - القسم - Department
   - رمز البرنامج - Program Code
   - الوصف - Description

3. اختر **منسق البرنامج** من القائمة المنسدلة
   - يظهر فقط المستخدمين الذين لديهم صلاحية `program_manager`

4. اضغط **"✓ حفظ"** - Click **"✓ Save"**

---

### 3. تعديل برنامج
### Editing a Program

1. حدد البرنامج من الجدول - Select program from table
2. اضغط **"✏️ تعديل"** أو اضغط مرتين على السطر
3. عدّل المعلومات المطلوبة
4. اضغط **"✓ حفظ"**

---

### 4. حذف برنامج
### Deleting a Program

⚠️ **تحذير:** حذف البرنامج سيؤثر على المقررات المرتبطة به!

1. حدد البرنامج من الجدول
2. اضغط **"🗑️ حذف"**
3. أكد الحذف

---

### 5. البحث عن برنامج
### Searching for a Program

استخدم مربع البحث للبحث في:
- اسم البرنامج - Program name
- اسم الكلية - College name
- اسم القسم - Department name

البحث يعمل بشكل فوري أثناء الكتابة.

---

### 6. عرض الإحصائيات
### Viewing Statistics

اضغط **"📊 إحصائيات"** لعرض:
- عدد البرامج الكلي - Total programs
- البرامج النشطة - Active programs
- البرامج المعطلة - Inactive programs
- عدد الكليات - Number of colleges
- عدد الأقسام - Number of departments

---

## <a name="management"></a>إدارة البرامج - Program Management

### إضافة منسق برنامج جديد
### Adding a New Program Coordinator

قبل إنشاء برنامج، تأكد من وجود مستخدم بصلاحية منسق برنامج:

Before creating a program, ensure there's a user with program coordinator permission:

1. اذهب إلى **"إدارة المستخدمين"** - Go to **"User Management"**
2. أضف مستخدم جديد أو عدّل مستخدم موجود
3. اختر دور **"منسق البرنامج"** (program_manager)
4. احفظ المستخدم
5. الآن يمكن اختياره كمنسق في إدارة البرامج

---

### نقل برنامج لمنسق آخر
### Transferring Program to Another Coordinator

1. افتح تعديل البرنامج
2. اختر المنسق الجديد من القائمة
3. احفظ التغييرات
4. ستتحول جميع الصلاحيات للمنسق الجديد

---

### تعطيل/تفعيل برنامج
### Deactivating/Activating a Program

1. افتح تعديل البرنامج
2. قم بتعيين أو إلغاء تعيين خيار **"نشط"**
3. احفظ التغييرات

البرامج المعطلة:
- لا تظهر في القوائم المنسدلة
- لا يمكن إضافة مقررات جديدة لها
- المقررات الموجودة تبقى متاحة للعرض فقط

---

## <a name="permissions"></a>الصلاحيات والأدوار - Permissions & Roles

### الأدوار المتاحة - Available Roles

#### 1. مدير النظام (Admin)
- صلاحيات كاملة
- إدارة البرامج الأكاديمية
- إدارة المستخدمين
- النسخ الاحتياطي
- سجل التدقيق

#### 2. منسق البرنامج (Program Coordinator)
**الصلاحيات الحالية - Current Permissions:**
- عرض برنامجه الأكاديمي
- إدارة المقررات ضمن برنامجه
- عرض تقارير البرنامج

**الصلاحيات المستقبلية - Future Permissions:**
- إضافة مقررات جديدة للبرنامج
- تعيين منسقي المقررات
- الموافقة على نتائج المقررات
- تصدير تقارير البرنامج

#### 3. منسق المقرر (Course Coordinator)
- إدارة المقرر المعين له
- إدارة شعب المقرر
- تعيين مدرسي الشعب

#### 4. مدرس الشعبة (Course Instructor)
- إدخال درجات الطلاب في شعبته
- عرض تقارير شعبته

---

## <a name="courses"></a>الربط مع المقررات - Course Integration

### كيف يرتبط المقرر بالبرنامج
### How Courses Link to Programs

**حالياً - Currently:**
المقررات موجودة ولكن غير مرتبطة بالبرامج بشكل مباشر.

**التحديث القادم - Next Update:**
سيتم تحديث نموذج المقرر ليحتوي على:

```python
class Course:
    def __init__(self):
        # ...existing fields...
        self.program_id = ""  # معرف البرنامج الأكاديمي
        # ...
```

**الفوائد - Benefits:**
1. كل مقرر سيكون مرتبط ببرنامج محدد
2. منسق البرنامج سيرى فقط مقررات برنامجه
3. التقارير ستكون مقسمة حسب البرنامج
4. إدارة أفضل للصلاحيات

---

## الملفات المُنشأة - Created Files

### النماذج - Models
```
models/
  └── academic_program.py      # نموذج البرنامج الأكاديمي
```

### المدراء - Managers
```
managers/
  └── academic_program_manager.py  # مدير البرامج الأكاديمية
```

### الواجهات - Dialogs
```
dialogs/
  └── academic_programs_dialog.py  # واجهة إدارة البرامج
```

### البيانات - Data
```
data/
  └── academic_programs/
      └── programs.json        # ملف تخزين البرامج
```

---

## أمثلة برمجية - Code Examples

### إنشاء برنامج برمجياً
### Creating a Program Programmatically

```python
from models.academic_program import AcademicProgram
from managers.academic_program_manager import program_manager

# إنشاء برنامج جديد
program = AcademicProgram(
    program_name_ar="بكالوريوس الإحصاء",
    program_name_en="Bachelor of Statistics",
    coordinator_id="user_12345",
    university_ar="جامعة تبوك",
    university_en="University of Tabuk",
    college_ar="كلية العلوم",
    college_en="College of Science",
    department_ar="قسم الإحصاء",
    department_en="Department of Statistics"
)

# حفظ البرنامج
program_manager.create_program(program)
```

### البحث عن البرامج
### Searching for Programs

```python
# البحث بالعربية
results = program_manager.search_programs("إحصاء", 'ar')

# البحث بالإنجليزية
results = program_manager.search_programs("Statistics", 'en')

# الحصول على برامج قسم معين
dept_programs = program_manager.get_programs_by_department("قسم الإحصاء")

# الحصول على برامج منسق معين
coordinator_programs = program_manager.get_programs_by_coordinator("user_12345")
```

---

## الأسئلة الشائعة - FAQ

### س: هل يمكن أن يكون الشخص منسقاً لأكثر من برنامج؟
**نعم!** يمكن تعيين نفس المستخدم كمنسق لعدة برامج.

### Q: Can one person coordinate multiple programs?
**Yes!** The same user can be assigned as coordinator for multiple programs.

---

### س: ماذا يحدث إذا حُذف المنسق من النظام؟
يُفضل تعيين منسق جديد للبرنامج قبل حذف المستخدم. إذا حُذف المنسق، سيظل البرنامج موجوداً ولكن بدون منسق نشط.

### Q: What happens if the coordinator is deleted from the system?
It's recommended to assign a new coordinator before deleting the user. If deleted, the program remains but without an active coordinator.

---

### س: هل يمكن استيراد البرامج من ملف Excel؟
**قريباً!** هذه ميزة مخطط لها في التحديثات القادمة.

### Q: Can programs be imported from an Excel file?
**Coming soon!** This feature is planned for future updates.

---

## التحديثات القادمة - Upcoming Updates

- [ ] ربط المقررات بالبرامج الأكاديمية
- [ ] تقارير مفصلة لكل برنامج
- [ ] صلاحيات محددة لمنسقي البرامج
- [ ] استيراد/تصدير البرامج من Excel
- [ ] نسخ برنامج موجود كقالب
- [ ] إحصائيات متقدمة للبرامج

---

## الدعم - Support

للمساعدة أو الإبلاغ عن مشاكل:
- راجع ملف `FIXES_APPLIED.txt`
- راجع ملف `SETUP_GUIDE.txt`
- تواصل مع مطور النظام

For help or bug reports:
- Review `FIXES_APPLIED.txt`
- Review `SETUP_GUIDE.txt`
- Contact the system developer

---

**تم التحديث:** 2026-01-07
**الإصدار:** 1.1
**المطور:** Hussein Youssef Abdelazim

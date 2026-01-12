# دليل الصلاحيات - Permissions Guide

## نظام الصلاحيات الكامل

### 1. منسق البرنامج (Program Coordinator)

**الصلاحيات**: جميع الصلاحيات التالية فقط داخل البرنامج الأكاديمي الذي هو منسق فيه

#### المرحلة الأولى:
- ✅ إنشاء مقرر جديد
- ✅ تعديل المقرر

#### المرحلة الثانية:
- ✅ إنشاء هذه المرحلة بجميع خطواتها الأربعة

#### المرحلة الثالثة:
- ❌ **لا يستطيع** إدخال درجات الشعب

#### صلاحيات إضافية:
- ✅ تعيين منسقي المقررات
- ✅ توزيع الشعب على الأعضاء
- ✅ عرض جميع التقارير الخاصة بشعب مقررات البرنامج
- ✅ واجهة تعرض نسبة الإنجاز لجميع شعب المقررات في برنامجه

#### كيفية التحقق من الصلاحيات:
```python
# التحقق من وصول منسق البرنامج للبرنامج
if user.has_access_to_program(program_id):
    # السماح بالوصول
    pass

# الحصول على البرامج المعينة للمستخدم
programs = user.get_assigned_programs()
```

---

### 2. منسق المقرر (Course Coordinator)

**الصلاحيات**: جميع الصلاحيات التالية فقط داخل شعب المقرر أو المقررات التي هو منسق فيها

#### المرحلة الأولى:
- 👁️ **عرض فقط** تقرير معلومات المقرر

#### المرحلة الثانية:
- 👁️ **عرض فقط** تقرير معلومات المقرر الخاصة بهذه المرحلة

#### المرحلة الثالثة:
- ❌ **لا يستطيع** إدخال درجات الشعب
- ✅ **يستطيع** إدخال الدرجات **فقط** إذا كانت الشعبة هو مدرس لها

#### صلاحيات إضافية:
- 👁️ عرض مدرسي شعب مقرراته (لا يمكن التعديل)
- ✅ عرض جميع التقارير الخاصة بالمقررات التي هو منسق لها
- ✅ واجهة تعرض نسبة الإنجاز لجميع شعب المقررات التي هو منسق لها

#### كيفية التحقق من الصلاحيات:
```python
# التحقق من وصول منسق المقرر للمقرر
if user.has_access_to_course(course_id):
    # السماح بالوصول
    pass

# الحصول على المقررات المعينة للمستخدم
courses = user.get_assigned_courses()

# التحقق من إمكانية إدخال الدرجات (إذا كان مدرساً للشعبة)
if user.has_access_to_section(course_id, section_name):
    # السماح بإدخال الدرجات
    pass
```

---

### 3. مدرس الشعبة (Section Instructor)

**الصلاحيات**: جميع الصلاحيات التالية فقط داخل شعب المقرر أو المقررات التي هو يدرس لها

#### المرحلة الأولى:
- 👁️ **عرض فقط** تقرير معلومات المقرر للشعب التي يدرس فيها

#### المرحلة الثانية:
- 👁️ **عرض فقط** تقرير معلومات المقرر الخاصة بهذه المرحلة للشعب التي يدرس فيها

#### المرحلة الثالثة:
- ✅ إدخال درجات الشعب
- ✅ هو **الوحيد** الذي يستطيع إدخال طلاب شعبته
- ✅ هو **الوحيد** الذي يستطيع إدخال درجات طلابه

#### صلاحيات إضافية:
- ✅ عرض جميع التقارير الخاصة بالشعب التي يقوم بتدريسها

#### كيفية التحقق من الصلاحيات:
```python
# التحقق من وصول مدرس الشعبة للشعبة
if user.has_access_to_section(course_id, section_name):
    # السماح بالوصول
    pass

# الحصول على الشعب المعينة للمستخدم
sections = user.get_assigned_sections()

# الحصول على شعب مقرر معين
course_sections = user.get_assigned_sections(course_id)
```

---

## الربط التلقائي للمستخدمين

### 1. ربط منسق البرنامج تلقائياً

عند تعيين منسق للبرنامج الأكاديمي في `AssignCoordinatorDialog`:
```python
# يتم تلقائياً:
# 1. إنشاء حساب مستخدم (إذا لم يكن موجوداً)
# 2. إضافة دور "program_coordinator"
# 3. ربط المستخدم بالبرنامج
access_control.assign_user_to_program(user_id, program_id)
```

### 2. ربط منسق المقرر تلقائياً

عند حفظ بيانات الفصل الدراسي في `SemesterManagementDialog`:
```python
# يتم تلقائياً:
# 1. إنشاء حساب مستخدم (إذا لم يكن موجوداً)
# 2. إضافة دور "course_coordinator"
# 3. ربط المستخدم بالمقرر
access_control.assign_user_to_course(user_id, course_id)
```

### 3. ربط مدرس الشعبة تلقائياً

عند حفظ بيانات الشعبة في `Stage3SectionInfoDialog`:
```python
# يتم تلقائياً:
# 1. إنشاء حساب مستخدم (إذا لم يكن موجوداً)
# 2. إضافة دور "section_instructor"
# 3. ربط المستخدم بالشعبة
access_control.assign_user_to_section(user_id, course_id, section_name)
```

---

## مثال على استخدام الصلاحيات في الكود

### مثال 1: التحقق من صلاحية عرض قائمة المقررات

```python
def get_accessible_courses(user, program_id):
    """الحصول على المقررات التي يستطيع المستخدم الوصول إليها"""

    if user.has_role('admin'):
        # المدير يستطيع الوصول لجميع المقررات
        return course_manager.get_all_courses()

    elif user.has_role('program_coordinator'):
        # منسق البرنامج يستطيع الوصول لمقررات برنامجه فقط
        if user.has_access_to_program(program_id):
            return course_manager.get_courses_by_program(program_id)
        return []

    elif user.has_role('course_coordinator'):
        # منسق المقرر يستطيع الوصول لمقرراته فقط
        return [course for course in course_manager.get_all_courses()
                if course.course_id in user.assigned_courses]

    elif user.has_role('section_instructor'):
        # مدرس الشعبة يستطيع الوصول للمقررات التي له فيها شعب
        return [course for course in course_manager.get_all_courses()
                if course.course_id in user.assigned_sections.keys()]

    return []
```

### مثال 2: التحقق من صلاحية إدخال الدرجات

```python
def can_edit_grades(user, course_id, section_name):
    """التحقق من إمكانية تعديل الدرجات"""

    if user.has_role('admin'):
        # المدير يستطيع تعديل جميع الدرجات
        return True

    elif user.has_role('section_instructor'):
        # مدرس الشعبة يستطيع تعديل درجات شعبته فقط
        return user.has_access_to_section(course_id, section_name)

    elif user.has_role('course_coordinator'):
        # منسق المقرر يستطيع تعديل الدرجات فقط إذا كان مدرساً للشعبة
        return user.has_access_to_section(course_id, section_name)

    return False
```

### مثال 3: التحقق من صلاحية إنشاء مقرر جديد

```python
def can_create_course(user, program_id):
    """التحقق من إمكانية إنشاء مقرر جديد"""

    if user.has_role('admin'):
        # المدير يستطيع إنشاء مقررات في أي برنامج
        return True

    elif user.has_role('program_coordinator'):
        # منسق البرنامج يستطيع إنشاء مقررات في برنامجه فقط
        return user.has_access_to_program(program_id)

    return False
```

---

## قاعدة البيانات

### بنية بيانات المستخدم في ملف users.json:

```json
{
  "users": [
    {
      "user_id": "user_001",
      "username": "H12345",
      "password_hash": "...",
      "full_name": "حسين يوسف",
      "email": "hussein@university.edu",
      "roles": ["program_coordinator"],
      "employee_id": "12345",
      "faculty_id": "faculty_001",
      "assigned_programs": ["program_001", "program_002"],
      "assigned_courses": [],
      "assigned_sections": {},
      "is_active": true
    },
    {
      "user_id": "user_002",
      "username": "A54321",
      "roles": ["course_coordinator", "section_instructor"],
      "assigned_programs": [],
      "assigned_courses": ["course_001"],
      "assigned_sections": {
        "course_001": ["Section 1", "Section 2"]
      }
    }
  ]
}
```

---

## ملاحظات مهمة

1. **المدير (admin)** لديه صلاحيات كاملة على جميع البرامج والمقررات والشعب
2. **منسق البرنامج** قد يكون منسقاً لأكثر من برنامج
3. **منسق المقرر** قد يكون منسقاً لأكثر من مقرر
4. **مدرس الشعبة** قد يدرس عدة شعب في عدة مقررات
5. المستخدم الواحد قد يجمع عدة أدوار (مثلاً: منسق مقرر ومدرس شعبة في نفس الوقت)

---

## API Reference

### User Model Methods

```python
# إدارة البرامج
user.assign_program(program_id: str) -> bool
user.unassign_program(program_id: str) -> bool
user.get_assigned_programs() -> List[str]
user.has_access_to_program(program_id: str) -> bool

# إدارة المقررات
user.assign_course(course_id: str) -> bool
user.unassign_course(course_id: str) -> bool
user.get_assigned_courses() -> List[str]
user.has_access_to_course(course_id: str) -> bool

# إدارة الشعب
user.assign_section(course_id: str, section_name: str) -> bool
user.unassign_section(course_id: str, section_name: str) -> bool
user.get_assigned_sections(course_id: str = None) -> Dict[str, List[str]]
user.has_access_to_section(course_id: str, section_name: str) -> bool
```

### AccessControl Methods

```python
# إدارة البرامج
access_control.assign_user_to_program(user_id: str, program_id: str) -> bool
access_control.unassign_user_from_program(user_id: str, program_id: str) -> bool
access_control.get_users_by_program(program_id: str) -> List[User]
access_control.get_program_coordinator_by_program(program_id: str) -> Optional[User]

# إدارة المقررات
access_control.assign_user_to_course(user_id: str, course_id: str) -> bool
access_control.unassign_user_from_course(user_id: str, course_id: str) -> bool
access_control.get_users_by_course(course_id: str) -> List[User]
access_control.get_course_coordinator_by_course(course_id: str) -> Optional[User]

# إدارة الشعب
access_control.assign_user_to_section(user_id: str, course_id: str, section_name: str) -> bool
access_control.unassign_user_from_section(user_id: str, course_id: str, section_name: str) -> bool
access_control.get_users_by_section(course_id: str, section_name: str) -> List[User]
access_control.get_section_instructors_by_section(course_id: str, section_name: str) -> List[User]
```

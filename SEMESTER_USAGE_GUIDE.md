# دليل استخدام نموذج Semester Management
# Semester Management Usage Guide

## المشكلة / Problem
قائمة المدرسين (Section Instructors) تظهر فارغة عند إعادة فتح نموذج Semester Management

## السبب / Cause
المدرسون لم يتم إضافتهم إلى القائمة قبل حفظ البيانات

## الخطوات الصحيحة للاستخدام / Correct Usage Steps

### عند إنشاء بيانات فصل دراسي جديد / Creating New Semester Data:

1. **افتح نموذج Semester Management**
   - من القائمة الرئيسية: اختر "Semester Management"
   - اختر المقرر المطلوب

2. **أدخل البيانات الأساسية**:
   - Academic Year: أدخل السنة الدراسية (مثل: 1447)
   - Semester: اختر الفصل الدراسي (First, Second, Summer)
   - Course Coordinator: أدخل اسم منسق المقرر

3. **إضافة المدرسين** (هذه الخطوة **مهمة جداً**):
   - في حقل "Instructor Name"، اكتب اسم المدرس الأول
   - اضغط على زر **"Add"** (الزر الأخضر)
   - يجب أن يظهر اسم المدرس في القائمة الكبيرة
   - كرر هذه الخطوة لكل مدرس تريد إضافته

   **مثال**:
   ```
   Instructor Name: [ Dr. Ahmed Ali        ] [Add]

   Section Instructors List:
   ┌────────────────────────────────────┐
   │ Dr. Ahmed Ali                      │
   │ Dr. Sara Mohammed                  │
   │ Dr. Fatima Hassan                  │
   └────────────────────────────────────┘
   ```

4. **تحديث المستويات المستهدفة** (اختياري):
   - في جدول CLO Target Levels، يمكنك تعديل المستويات المستهدفة
   - القيم الافتراضية تُحمل من بيانات المقرر

5. **احفظ البيانات**:
   - اضغط على زر **"Save"**
   - ستظهر رسالة تأكيد بنجاح الحفظ
   - ستُغلق النافذة تلقائياً

### عند تعديل بيانات فصل دراسي موجود / Editing Existing Semester Data:

1. **افتح نموذج Semester Management**
   - سيتم تحميل آخر بيانات فصلية تلقائياً
   - ستظهر السنة الدراسية والفصل والمنسق
   - ستظهر قائمة المدرسين المحفوظة سابقاً

2. **تعديل البيانات**:
   - لإضافة مدرس جديد: اكتب الاسم واضغط "Add"
   - لحذف مدرس: حدد الاسم من القائمة واضغط "Remove Selected"
   - لتعديل المستويات المستهدفة: غيّر القيم في جدول CLO Target Levels

3. **احفظ التعديلات**:
   - اضغط على زر "Save"

## ملاحظات مهمة / Important Notes

⚠️ **يجب الضغط على زر "Add"**
- مجرد كتابة اسم المدرس في حقل "Instructor Name" **لا يكفي**
- يجب الضغط على زر **"Add"** حتى يُضاف الاسم إلى القائمة
- القائمة الكبيرة (Listbox) هي التي تُحفظ في قاعدة البيانات

✅ **التحقق من الحفظ**
- بعد الحفظ، أعد فتح نموذج Semester Management
- تحقق من أن قائمة المدرسين تحتوي على الأسماء التي أضفتها
- إذا كانت القائمة فارغة، معناه أنك لم تضغط على زر "Add"

📝 **زر "Load Semester Data"**
- هذا الزر لتحميل بيانات فصل دراسي مختلف يدوياً
- عند فتح النافذة، يتم تحميل آخر بيانات تلقائياً
- استخدم هذا الزر فقط إذا أردت تحميل فصل دراسي آخر

## مثال عملي / Practical Example

### إضافة 3 مدرسين:

1. اكتب "Dr. Ali Hassan" → اضغط Add
2. اكتب "Dr. Sara Ahmed" → اضغط Add
3. اكتب "Dr. Mohammed Ali" → اضغط Add

### النتيجة المتوقعة:
```
Section Instructors List:
┌────────────────────────────────────┐
│ Dr. Ali Hassan                     │
│ Dr. Sara Ahmed                     │
│ Dr. Mohammed Ali                   │
└────────────────────────────────────┘
```

الآن اضغط Save - ستُحفظ الأسماء الثلاثة!

---

# للمطورين / For Developers

## البيانات المحفوظة / Saved Data Structure

```json
{
  "semester_data": {
    "1447_First": {
      "academic_year": "1447",
      "semester": "First",
      "course_coordinator": "Dr. Dalia Najar",
      "instructors": [
        "Dr. Ali Hassan",
        "Dr. Sara Ahmed",
        "Dr. Mohammed Ali"
      ],
      "clo_target_levels": {
        "K1": 62.0,
        "K2": 60.0
      }
    }
  }
}
```

## الكود المسؤول / Responsible Code

- **الحفظ**: `semester_management_dialog.py:497`
  ```python
  instructors = list(self.instructors_listbox.get(0, tk.END))
  ```

- **التحميل**: `semester_management_dialog.py:431-433`
  ```python
  self.instructors_listbox.delete(0, tk.END)
  for instructor in semester_data.instructors:
      self.instructors_listbox.insert(tk.END, instructor)
  ```

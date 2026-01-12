# دليل استخدام ميزة معاينة وتحميل التقرير
# Report Preview & Download Feature Guide

## نظرة عامة | Overview

تم تحديث تقرير إنجاز الطلاب في المخرجات ليتيح للمستخدم معاينة التقرير أولاً قبل حفظه.

The Students CLO Achievement Report has been updated to allow users to preview the report before saving it.

---

## كيفية الاستخدام | How to Use

### الخطوات | Steps:

1. **فتح نافذة التقرير | Open Report Dialog**
   - من القائمة الرئيسية: `📊 التقارير` → `👥 تقرير إنجاز الطلاب في المخرجات`
   - From main menu: `📊 Reports` → `👥 Students CLO Achievement Report`

2. **اختيار المقرر | Select Course**
   - اختر المقرر من القائمة المنسدلة
   - Select the course from the dropdown list

3. **اختيار الشعب | Select Sections**
   - اختر شعبة واحدة أو أكثر (Ctrl + Click لاختيار متعدد)
   - Select one or more sections (Ctrl + Click for multiple selection)

4. **معاينة التقرير | Preview Report**
   - اضغط زر `👁 معاينة وتحميل التقرير`
   - Click the `👁 Preview & Download Report` button
   - سيتم فتح التقرير تلقائياً في برنامج قراءة PDF الافتراضي
   - The report will open automatically in your default PDF reader

5. **حفظ التقرير (اختياري) | Save Report (Optional)**
   - بعد المعاينة، ستظهر رسالة تسأل: "هل تريد حفظ نسخة من التقرير؟"
   - After preview, a message will ask: "Do you want to save a copy of the report?"
   - إذا اخترت "نعم":
     - اختر مكان حفظ الملف
     - سيتم حفظ نسخة دائمة من التقرير
   - If you choose "Yes":
     - Choose where to save the file
     - A permanent copy will be saved

---

## مميزات التقرير | Report Features

### الجزء الأول: الجدول الملخص | Part 1: Summary Table

يعرض لكل مخرج:
- عدد الطلاب الكلي
- عدد الذين حققوا المخرج
- عدد الذين لم يحققوا المخرج
- نسبة الإنجاز (مع تلوين تلقائي)

Shows for each CLO:
- Total number of students
- Number who achieved the CLO
- Number who did not achieve the CLO
- Achievement percentage (with automatic coloring)

**نظام الألوان | Color System:**
- 🟢 أخضر (≥80%): أداء ممتاز | Green (≥80%): Excellent performance
- 🟡 أصفر (60-79%): أداء جيد | Yellow (60-79%): Good performance
- 🔴 أحمر (<60%): يحتاج تحسين | Red (<60%): Needs improvement

### الجزء الثاني: تفاصيل الطلاب | Part 2: Student Details

لكل مخرج، يعرض قائمة بالطلاب الذين لم يحققوه:
- الرقم الجامعي
- الدرجة المحققة
- الدرجة الكلية للمخرج
- النسبة المئوية

For each CLO, shows list of students who did not achieve it:
- Student ID
- Score achieved
- Total CLO score
- Percentage

---

## معلومات الرأس | Header Information

يتضمن رأس التقرير:
- رمز المقرر واسمه
- رقم الشعبة والسنة الدراسية والفصل
- اسم أستاذ الشعبة
- تاريخ التقرير

The report header includes:
- Course code and title
- Section number, academic year, and semester
- Section instructor name
- Report date

---

## ملاحظات تقنية | Technical Notes

1. **الملف المؤقت | Temporary File**
   - يتم إنشاء ملف PDF مؤقت للمعاينة
   - يُحذف تلقائياً بعد 5 ثوانٍ من الإغلاق
   - A temporary PDF file is created for preview
   - Automatically deleted 5 seconds after closing

2. **الخصوصية | Privacy**
   - التقرير لا يعرض أسماء الطلاب، فقط أرقامهم الجامعية
   - The report does not show student names, only their IDs

3. **الشعب المتعددة | Multiple Sections**
   - يمكن اختيار أكثر من شعبة لإنشاء تقرير موحد
   - Multiple sections can be selected to create a combined report

---

## الأمثلة | Examples

### مثال 1: معاينة بدون حفظ | Example 1: Preview Without Saving
```
1. اختر المقرر STAT1204
2. اختر الشعبة 4318
3. اضغط "معاينة وتحميل التقرير"
4. راجع التقرير
5. اضغط "لا" عند السؤال عن الحفظ
```

### مثال 2: معاينة مع الحفظ | Example 2: Preview With Saving
```
1. اختر المقرر STAT1204
2. اختر شعبتين (317 و 4318)
3. اضغط "معاينة وتحميل التقرير"
4. راجع التقرير
5. اضغط "نعم" للحفظ
6. اختر مكان الحفظ (مثل: Documents/Reports/)
```

---

## استكشاف الأخطاء | Troubleshooting

### المشكلة: لا يفتح التقرير تلقائياً
**الحل:**
- تأكد من وجود برنامج لقراءة PDF على جهازك
- Make sure you have a PDF reader installed

### المشكلة: خطأ عند إنشاء التقرير
**الحل:**
- تأكد من اختيار المقرر والشعبة
- تأكد من وجود طلاب في الشعبة المختارة
- Ensure course and section are selected
- Ensure the selected section has students

---

## التحديثات المستقبلية | Future Updates

- إضافة خيار طباعة مباشرة
- إضافة تصدير بصيغ أخرى (Excel, Word)
- Direct printing option
- Export to other formats (Excel, Word)

# دليل استخدام ترويسة التقارير
# Report Header User Guide

## نظرة عامة | Overview

تم إضافة نظام جديد لإدارة ترويسة التقارير في النظام. يتيح هذا النظام:

A new report header management system has been added. This system allows:

- تحميل شعار الجامعة | Upload university logo
- تعديل النصوص بالإنجليزية والعربية | Edit text in English and Arabic
- معاينة الترويسة قبل الحفظ | Preview header before saving
- استخدام الترويسة تلقائياً في جميع التقارير | Automatically use header in all reports

---

## كيفية الوصول | How to Access

### من القائمة الرئيسية | From Main Menu

1. افتح البرنامج | Open the application
2. من شريط القوائم اختر: **الإعدادات** | From menu bar select: **Settings**
3. اختر: **ترويسة التقارير** | Select: **Report Header**

---

## واجهة الإعدادات | Settings Interface

### 1. قسم المعاينة | Preview Section

- يعرض شكل الترويسة الفعلي | Shows actual header appearance
- يتحدث تلقائياً عند تغيير أي بيانات | Updates automatically when data changes

### 2. قسم الشعار | Logo Section

**تحميل شعار | Upload Logo:**
- اضغط على زر "📁 تحميل شعار" | Click "📁 Upload Logo" button
- اختر صورة الشعار (PNG, JPG, GIF, BMP) | Select logo image (PNG, JPG, GIF, BMP)
- الحجم الموصى به: 300x300 بكسل | Recommended size: 300x300 pixels
- سيتم نسخ الصورة تلقائياً إلى مجلد البيانات | Image will be copied automatically to data folder

**حذف الشعار | Remove Logo:**
- اضغط على زر "🗑 حذف الشعار" | Click "🗑 Remove Logo" button

### 3. النصوص الإنجليزية | English Text

يمكنك تعديل: | You can edit:
- University Name | اسم الجامعة
- Faculty Name | اسم الكلية
- Department Name | اسم القسم

### 4. النصوص العربية | Arabic Text

يمكنك تعديل: | You can edit:
- اسم الجامعة | University Name
- اسم الكلية | Faculty Name
- اسم القسم | Department Name

---

## الحفظ والإلغاء | Save and Cancel

- **حفظ | Save:** حفظ جميع التغييرات | Save all changes
- **إلغاء | Cancel:** إغلاق النافذة بدون حفظ | Close window without saving

---

## البنية التقنية | Technical Structure

### الملفات الجديدة | New Files

1. **models/report_header.py**
   - نموذج البيانات لإعدادات الترويسة
   - Data model for header settings

2. **dialogs/report_header_dialog.py**
   - واجهة المستخدم لتحرير الإعدادات
   - User interface for editing settings

3. **utils/report_utils.py**
   - دوال مساعدة لإضافة الترويسة للتقارير
   - Helper functions to add header to reports

4. **data/report_header.json**
   - ملف حفظ الإعدادات (يُنشأ تلقائياً)
   - Settings save file (created automatically)

5. **data/images/**
   - مجلد حفظ صور الشعار
   - Logo images folder

---

## استخدام الترويسة في التقارير | Using Header in Reports

### طريقة 1: باستخدام Elements | Method 1: Using Elements

```python
from utils.report_utils import add_report_header

elements = []
add_report_header(elements, language='en', orientation='portrait')
# أضف باقي عناصر التقرير
# Add rest of report elements
```

### طريقة 2: باستخدام Canvas | Method 2: Using Canvas

```python
from utils.report_utils import create_header_frame_for_canvas

def first_page(canvas, doc):
    create_header_frame_for_canvas(canvas, doc, language='en')

doc.build(elements, onFirstPage=first_page)
```

---

## أمثلة | Examples

### مثال كامل | Complete Example

راجع الملف: **test_report_header.py**
See file: **test_report_header.py**

---

## الإعدادات الافتراضية | Default Settings

عند أول استخدام، القيم الافتراضية هي:
On first use, default values are:

**English:**
- University: University of Tabuk
- Faculty: Faculty of Science
- Department: Department of Statistics

**Arabic:**
- الجامعة: جامعة تبوك
- الكلية: كلية العلوم
- القسم: قسم الإحصاء

---

## ملاحظات مهمة | Important Notes

1. **تنسيق الشعار | Logo Format:**
   - يُفضل استخدام صور PNG بخلفية شفافة
   - Prefer PNG images with transparent background
   - الحجم الأمثل: 300x300 بكسل
   - Optimal size: 300x300 pixels

2. **موقع الترويسة | Header Location:**
   - تظهر الترويسة في الصفحة الأولى فقط
   - Header appears on first page only
   - تحفظ مساحة 4 سم في أعلى الصفحة
   - Reserves 4 cm space at top of page

3. **التوافق | Compatibility:**
   - تعمل الترويسة مع جميع التقارير تلقائياً
   - Header automatically works with all reports
   - تم تطبيق الترويسة على جميع التقارير الموجودة:
   - Header applied to all existing reports:
     * تقرير قياس مخرجات التعلم (CLO Assessment)
     * تقرير قياس نواتج التعلم المجمع (Aggregated CLO)
     * تقرير إنجاز الطلاب (Students Achievement)
     * تقرير المرحلة الأولى (Stage 1 Report)
     * تقرير لوحة البيانات (Dashboard Report)

4. **الأمان | Security:**
   - الإعدادات محفوظة محلياً
   - Settings are saved locally
   - لا يتم إرسال أي بيانات عبر الإنترنت
   - No data is sent over internet

---

## الدعم الفني | Technical Support

في حالة وجود أي مشاكل أو استفسارات:
For any issues or questions:

- راجع ملف الأخطاء | Check error log
- تواصل مع الدعم الفني | Contact technical support
- البريد الإلكتروني | Email: hussein.abdelazim@ut.edu.sa

---

## التحديثات المستقبلية | Future Updates

التحسينات المخططة:
Planned improvements:

- دعم شعارات متعددة | Multiple logos support
- خيارات تنسيق إضافية | Additional formatting options
- قوالب جاهزة | Ready templates
- تصدير/استيراد الإعدادات | Export/import settings

---

**تم بحمد الله**
**Alhamdulillah - All praise is due to Allah**

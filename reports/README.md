# تقارير النظام - System Reports

هذا المجلد يحتوي على مولدات التقارير بصيغة PDF.

## التقارير المتوفرة

### 1. تقرير معلومات المقرر - Stage 1 Report
**الملف:** `stage1_report_generator.py`

يولد تقرير PDF كامل يحتوي على:
- معلومات المقرر الأساسية
- مخرجات التعلم (CLOs)
- المواضيع الدراسية
- أنشطة التقييم

**الاستخدام:**
```python
from reports import Stage1ReportGenerator

generator = Stage1ReportGenerator(course, language='en')
generator.generate_report('output.pdf')
```

### 2. تقارير أوراق الأنشطة - Activity Sheets
**الملف:** `activity_sheet_generator.py`

يولد ورقة PDF لنشاط محدد حسب النموذج المعتمد، تحتوي على:
- ترويسة الجامعة والقسم
- عنوان النشاط ورمز المقرر
- جدول يوضح توزيع النشاط على:
  - المواضيع (Topics)
  - المخرجات (CLOs)
  - الدرجات (Marks)

**الاستخدام:**
```python
from reports import generate_activity_sheet

# لنشاط واحد
generate_activity_sheet(course, "Mid Exam", "output.pdf", language='en')

# لعدة أنشطة
for activity in course.activities:
    filename = f"{activity.name}.pdf"
    generate_activity_sheet(course, activity.name, filename, language='en')
```

**الوصول من القائمة:**
- قائمة التقارير → تقارير أوراق الأنشطة
- Reports → Activity Sheets

## البنية

```
reports/
├── __init__.py                      # تصدير المولدات
├── stage1_report_generator.py       # تقرير المرحلة الأولى
├── activity_sheet_generator.py      # تقارير أوراق الأنشطة
├── generated/                       # مجلد التقارير المولدة
│   ├── activity_sheets/            # أوراق الأنشطة
│   └── [course]_Report_[date].pdf  # تقارير المقررات
└── README.md                        # هذا الملف
```

## المتطلبات

- reportlab
- arabic-reshaper
- python-bidi

## ملاحظات

1. جميع التقارير تدعم اللغتين العربية والإنجليزية
2. يتم حفظ التقارير في مجلد `generated/`
3. أسماء الملفات تتضمن التاريخ والوقت لتجنب التكرار
4. الخطوط العربية يجب أن تكون موجودة في مجلد `fonts/`

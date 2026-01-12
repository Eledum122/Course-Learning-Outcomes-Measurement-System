# نظام قياس مخرجات التعلم - نسخة الويب
# CLOs Measurement System - Web Version

## 📋 نظرة عامة / Overview

تطبيق ويب متكامل لإدارة وقياس مخرجات التعلم للمقررات والبرامج الأكاديمية، مبني باستخدام **Streamlit**.

An integrated web application for managing and measuring learning outcomes for academic courses and programs, built with **Streamlit**.

---

## 🚀 التثبيت والتشغيل / Installation & Setup

### 1. تثبيت المتطلبات / Install Requirements

```bash
pip install -r requirements_streamlit.txt
```

### 2. تشغيل التطبيق / Run the Application

```bash
streamlit run streamlit_app.py
```

أو باستخدام / Or using:

```bash
python -m streamlit run streamlit_app.py
```

### 3. فتح التطبيق / Open the Application

بعد تشغيل الأمر، سيفتح المتصفح تلقائياً على:
After running the command, the browser will automatically open at:

```
http://localhost:8501
```

---

## 🔑 بيانات تسجيل الدخول الافتراضية / Default Login Credentials

### المدير / Admin
- **اسم المستخدم / Username:** `admin`
- **كلمة المرور / Password:** `admin123`

### منسق برنامج / Program Coordinator
- **اسم المستخدم / Username:** `coordinator`
- **كلمة المرور / Password:** `coord123`

### منسق مقرر / Course Coordinator
- **اسم المستخدم / Username:** `course_coord`
- **كلمة المرور / Password:** `course123`

### مدرس شعبة / Section Instructor
- **اسم المستخدم / Username:** `instructor`
- **كلمة المرور / Password:** `instr123`

---

## 📁 هيكل المشروع / Project Structure

```
CLOs_Measurement_System_03/
├── streamlit_app.py              # الملف الرئيسي / Main file
├── requirements_streamlit.txt    # المتطلبات / Requirements
├── .streamlit/
│   ├── config.toml              # إعدادات Streamlit
│   └── secrets.toml             # الأسرار (لا ترفع على GitHub)
├── models/                       # النماذج الموجودة / Existing models
├── utils/                        # الوظائف المساعدة / Utilities
├── translations.py               # الترجمات / Translations
└── clos_system.db               # قاعدة البيانات / Database
```

---

## ✨ المميزات الحالية / Current Features

### ✅ تم الإنجاز / Completed

1. **نظام تسجيل الدخول / Login System**
   - دعم كامل للعربية والإنجليزية
   - أربعة أدوار مختلفة
   - واجهة سهلة وواضحة

2. **لوحة التحكم / Dashboard**
   - معلومات المستخدم
   - بطاقات إحصائية
   - قائمة جانبية تفاعلية

3. **القوائم حسب الصلاحيات / Role-based Menus**
   - قوائم مخصصة لكل دور
   - صلاحيات محكمة

### 🚧 قيد التطوير / Under Development

- إدارة المستخدمين / Users Management
- إدارة البرامج / Programs Management
- إدارة المقررات / Courses Management
- إدخال الدرجات / Grades Entry
- التقارير / Reports
- التقييم / Assessment

---

## 🎨 التخصيص / Customization

### تغيير الألوان / Change Colors

عدل ملف `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"    # اللون الأساسي
backgroundColor = "#ffffff"  # لون الخلفية
```

### إضافة لغة جديدة / Add New Language

عدل ملف `translations.py` وأضف اللغة الجديدة في كل قاموس:

```python
'key_name': {
    'ar': 'النص بالعربية',
    'en': 'Text in English',
    'fr': 'Texte en français'  # إضافة لغة جديدة
}
```

---

## 🌐 النشر على الإنترنت / Deploy to Internet

### Streamlit Community Cloud (مجاني / Free)

1. ارفع المشروع على GitHub
2. اذهب إلى [share.streamlit.io](https://share.streamlit.io)
3. اربط حساب GitHub
4. اختر المستودع والفرع
5. اضغط Deploy

### Heroku

```bash
# تثبيت Heroku CLI
heroku login
heroku create your-app-name
git push heroku main
```

### Docker

```bash
# إنشاء Dockerfile
docker build -t clos-system .
docker run -p 8501:8501 clos-system
```

---

## 📝 ملاحظات مهمة / Important Notes

1. **الأمان / Security:**
   - غير كلمات المرور الافتراضية في الإنتاج
   - احذف ملف `secrets.toml` من git
   - استخدم HTTPS في الإنتاج

2. **قاعدة البيانات / Database:**
   - SQLite للتطوير والاختبار
   - انتقل إلى PostgreSQL للإنتاج

3. **الأداء / Performance:**
   - استخدم `@st.cache_data` و `@st.cache_resource` للبيانات الثابتة
   - راقب استخدام الذاكرة للملفات الكبيرة

---

## 🐛 حل المشاكل / Troubleshooting

### المشكلة: التطبيق لا يعمل
**الحل:** تأكد من تثبيت جميع المتطلبات:
```bash
pip install -r requirements_streamlit.txt
```

### المشكلة: العربية لا تظهر بشكل صحيح
**الحل:** تأكد من وجود خط Cairo في CSS (موجود افتراضياً)

### المشكلة: قاعدة البيانات لا تعمل
**الحل:** تأكد من وجود ملف `clos_system.db` في نفس المجلد

---

## 📧 الدعم / Support

للمساعدة والدعم:
- البريد الإلكتروني / Email: support@clos-system.com
- المستودع / Repository: [GitHub](https://github.com/your-repo)

---

## 📄 الترخيص / License

هذا المشروع مرخص بموجب MIT License.
This project is licensed under the MIT License.

---

## 🙏 شكر وتقدير / Acknowledgments

- **Streamlit** - إطار العمل الرائع
- **Python Community** - الدعم المستمر
- جميع المساهمين في المشروع

---

**آخر تحديث / Last Update:** 2026-01-11
**الإصدار / Version:** 2.0 (Streamlit Web Version)

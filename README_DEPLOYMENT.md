# دليل نشر التطبيق على Streamlit Cloud
# Deployment Guide for Streamlit Cloud

## ✅ المشاكل التي تم حلها / Problems Fixed

### 1. مشكلة Python 3.13 مع Pillow
**المشكلة:** Streamlit Cloud يستخدم Python 3.13 وPillow 10.1.0 غير متوافق
**الحل:** تحديث Pillow إلى 10.2.0+ وإضافة ملف `runtime.txt` لتحديد Python 3.11

### 2. مشكلة tkcalendar (Tkinter)
**المشكلة:** tkcalendar يعتمد على Tkinter ولا يعمل في بيئة السيرفر
**الحل:** إزالة tkcalendar من requirements.txt (غير مطلوب للنسخة Web)

---

## 📋 الملفات المطلوبة للنشر / Required Files

تأكد من وجود هذه الملفات في المستودع:

- ✅ `streamlit_app.py` - الملف الرئيسي
- ✅ `requirements.txt` - المكتبات المطلوبة (محدث)
- ✅ `runtime.txt` - إصدار Python (3.11)
- ✅ `packages.txt` - المكتبات النظامية
- ✅ `.streamlit/config.toml` - إعدادات Streamlit
- ✅ `clos_system.db` - قاعدة البيانات
- ✅ `models/` - النماذج
- ✅ `translations.py` - الترجمات

---

## 🚀 خطوات النشر / Deployment Steps

### 1. رفع الكود على GitHub

```bash
# تهيئة Git (إذا لم يكن مهيأ)
git init
git add .
git commit -m "Initial commit - Streamlit web version"

# إضافة المستودع البعيد
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### 2. النشر على Streamlit Cloud

1. اذهب إلى: https://share.streamlit.io
2. سجل دخول بحساب GitHub
3. اضغط "New app"
4. اختر:
   - **Repository:** YOUR_USERNAME/YOUR_REPO
   - **Branch:** main
   - **Main file path:** streamlit_app.py
5. اضغط "Deploy"
6. انتظر 2-3 دقائق للبناء

---

## ⚙️ الإعدادات المهمة / Important Settings

### إعدادات قاعدة البيانات

قد تحتاج لإضافة secrets في Streamlit Cloud:

1. اذهب إلى App settings → Secrets
2. أضف:

```toml
[database]
path = "clos_system.db"

[admin]
default_username = "admin"
default_password = "YOUR_SECURE_PASSWORD_HERE"
```

⚠️ **مهم:** غير كلمة المرور الافتراضية في الإنتاج!

---

## 🔍 حل المشاكل الشائعة / Troubleshooting

### المشكلة 1: خطأ في تثبيت Pillow
```
ERROR: Failed building wheel for Pillow
```

**الحل:**
- تأكد من أن `runtime.txt` يحتوي على `python-3.11`
- تأكد من أن `requirements.txt` يحتوي على `Pillow>=10.2.0`

### المشكلة 2: خطأ ModuleNotFoundError
```
ModuleNotFoundError: No module named 'tkcalendar'
```

**الحل:**
- تأكد من إزالة `tkcalendar` من `requirements.txt`
- النسخة Web لا تحتاج Tkinter

### المشكلة 3: خطأ في قاعدة البيانات
```
sqlite3.OperationalError: unable to open database file
```

**الحل:**
- تأكد من رفع ملف `clos_system.db` على GitHub
- أو أنشئ قاعدة بيانات جديدة في أول تشغيل

### المشكلة 4: خطأ في الترجمات
```
ModuleNotFoundError: No module named 'translations'
```

**الحل:**
- تأكد من رفع ملف `translations.py` على GitHub
- تأكد من رفع مجلد `models/` بالكامل

---

## 📦 محتوى requirements.txt الصحيح

```txt
# CLOs Measurement System Requirements - Streamlit Cloud Compatible
# Updated for Python 3.13 compatibility

# Streamlit Framework
streamlit>=1.32.0

# Authentication
streamlit-authenticator>=0.3.1

# PDF Generation
reportlab>=4.0.7

# Excel Support
openpyxl>=3.1.2
python-docx>=1.1.0

# Image Processing (for reports) - Updated for Python 3.13
Pillow>=10.2.0

# Arabic Text Support
arabic-reshaper>=3.0.0
python-bidi>=0.6.0

# Data Handling
python-dateutil>=2.8.2
```

---

## 🔐 الأمان / Security

### قبل النشر:

1. ✅ غير كلمات المرور الافتراضية
2. ✅ احذف ملف `.streamlit/secrets.toml` من Git
3. ✅ أضف secrets في Streamlit Cloud مباشرة
4. ✅ تأكد من `.gitignore` يتضمن `secrets.toml`

### بعد النشر:

1. اختبر تسجيل الدخول
2. اختبر جميع الأدوار
3. تأكد من عمل قاعدة البيانات
4. راقب الأخطاء في لوج التطبيق

---

## 🌐 الرابط النهائي / Final URL

بعد النشر، سيكون التطبيق متاحاً على:
```
https://YOUR-APP-NAME.streamlit.app
```

يمكنك تخصيص الرابط من إعدادات التطبيق.

---

## 📊 المراقبة / Monitoring

### عرض السجلات (Logs):
1. اذهب إلى: https://share.streamlit.io
2. افتح تطبيقك
3. اضغط "Manage app" → "Logs"

### عرض الاستخدام:
- CPU Usage
- Memory Usage
- Active Users
- Error Rate

---

## 🔄 التحديثات / Updates

لتحديث التطبيق بعد النشر:

```bash
# عدل الكود محلياً
git add .
git commit -m "Update: description of changes"
git push origin main

# Streamlit Cloud سيعيد البناء تلقائياً في 1-2 دقيقة
```

---

## 🆘 الدعم / Support

إذا واجهت مشاكل:

1. **راجع السجلات (Logs)** أولاً
2. **تأكد من جميع الملفات موجودة** على GitHub
3. **تحقق من requirements.txt** أنه صحيح
4. **راجع Streamlit Community Forum**: https://discuss.streamlit.io

---

## ✅ قائمة التحقق النهائية / Final Checklist

قبل النشر، تأكد من:

- [ ] تم رفع جميع الملفات على GitHub
- [ ] `requirements.txt` لا يحتوي على tkcalendar
- [ ] `runtime.txt` يحدد Python 3.11
- [ ] `clos_system.db` موجود
- [ ] `.gitignore` يستثني secrets.toml
- [ ] تم تغيير كلمات المرور الافتراضية
- [ ] تم اختبار التطبيق محلياً
- [ ] تم قراءة جميع التعليمات

---

## 🎉 مبروك!

إذا اتبعت جميع الخطوات، تطبيقك الآن على الإنترنت ويمكن الوصول إليه من أي مكان! 🌍

---

**تاريخ آخر تحديث:** 2026-01-11
**الإصدار:** 2.0 (Streamlit Cloud Ready)

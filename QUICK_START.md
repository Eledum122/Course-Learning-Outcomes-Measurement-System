# دليل البدء السريع / Quick Start Guide

## 🎯 خطوات سريعة للبدء / Quick Steps to Start

### 1️⃣ تشغيل التطبيق / Run the Application

افتح Terminal/Command Prompt واكتب:
```bash
streamlit run streamlit_app.py
```

سيفتح المتصفح تلقائياً على: `http://localhost:8501`

---

### 2️⃣ تسجيل الدخول / Login

استخدم أحد الحسابات التالية للتجربة:

| الدور / Role | اسم المستخدم / Username | كلمة المرور / Password |
|-------------|------------------------|----------------------|
| 👑 مدير / Admin | `admin` | `admin123` |
| 🎓 منسق برنامج / Program Coordinator | `coordinator` | `coord123` |
| 📚 منسق مقرر / Course Coordinator | `course_coord` | `course123` |
| 👨‍🏫 مدرس / Instructor | `instructor` | `instr123` |

---

### 3️⃣ استكشف الواجهة / Explore the Interface

#### القائمة الجانبية / Sidebar
- معلومات المستخدم الحالي
- القوائم حسب الدور
- تغيير اللغة
- تسجيل الخروج

#### لوحة التحكم / Dashboard
- بطاقات الإحصائيات
- معلومات المستخدم التفصيلية
- رسالة الترحيب

---

## 🌐 تغيير اللغة / Change Language

من أعلى صفحة تسجيل الدخول، اختر:
- 🇸🇦 العربية (Arabic)
- 🇬🇧 English

أو من القائمة الجانبية بعد تسجيل الدخول، اضغط:
- 🌐 تغيير اللغة / Change Language

---

## 🔧 حل المشاكل السريع / Quick Troubleshooting

### المشكلة: الأمر streamlit غير موجود
```bash
pip install streamlit
```

### المشكلة: خطأ في استيراد الوحدات
```bash
pip install -r requirements_streamlit.txt
```

### المشكلة: المنفذ 8501 مستخدم
```bash
streamlit run streamlit_app.py --server.port 8502
```

### المشكلة: التطبيق بطيء
- امسح الـ cache: اضغط `C` في Terminal
- أو أعد تشغيل التطبيق

---

## 📱 استخدام على أجهزة أخرى / Use on Other Devices

### على نفس الشبكة:
1. شغل التطبيق
2. احصل على IP الجهاز:
   ```bash
   ipconfig  # Windows
   ifconfig  # Mac/Linux
   ```
3. افتح على الجهاز الآخر:
   ```
   http://192.168.1.X:8501
   ```
   (استبدل X برقم IP الخاص بك)

---

## 🎨 تخصيص المظهر / Customize Appearance

عدل ملف `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"     # لون الأزرار الرئيسية
backgroundColor = "#ffffff"   # لون الخلفية
textColor = "#262730"        # لون النص
```

ثم أعد تشغيل التطبيق.

---

## 🚀 نشر على الإنترنت / Deploy Online

### الطريقة الأسهل: Streamlit Cloud (مجاني!)

1. ارفع الكود على GitHub
2. اذهب إلى: https://share.streamlit.io
3. سجل دخول بحساب GitHub
4. اختر المستودع (Repository)
5. اضغط Deploy
6. انتظر دقيقتين... جاهز! 🎉

### ملاحظات مهمة قبل النشر:
- ✅ غير كلمات المرور الافتراضية
- ✅ احذف ملف `.streamlit/secrets.toml` من Git
- ✅ أضف `.streamlit/secrets.toml` إلى `.gitignore`

---

## 📖 للمزيد من التفاصيل / For More Details

- 📄 README_STREAMLIT.md - دليل شامل
- 🏗️ ARCHITECTURE.md - بنية التطبيق
- 📝 كيفية_التشغيل.txt - تعليمات عربية

---

## 💡 نصائح الاستخدام / Usage Tips

### ⌨️ اختصارات لوحة المفاتيح:
- `R` - إعادة تشغيل التطبيق
- `C` - مسح الـ cache
- `Ctrl+C` - إيقاف التطبيق

### 🎯 أفضل الممارسات:
- استخدم Chrome أو Firefox أو Edge الحديث
- لا تغلق نافذة Terminal أثناء التشغيل
- احفظ التغييرات قبل إعادة التشغيل
- راجع الأخطاء في Terminal

---

**استمتع باستخدام النظام! 🎉**

**آخر تحديث / Last Update:** 2026-01-11

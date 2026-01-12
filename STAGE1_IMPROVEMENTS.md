# تحسينات المرحلة الأولى - نظام قياس مخرجات التعلم
# Stage 1 Improvements - CLOs Measurement System

**التاريخ / Date:** 2025-12-25
**الإصدار / Version:** 1.0

---

## 📋 ملخص التحسينات / Summary of Improvements

تم تحسين المرحلة الأولى من نظام قياس مخرجات التعلم بإضافة ميزة **التبديل الديناميكي بين اللغتين العربية والإنجليزية** مع تحسينات أخرى في واجهة المستخدم.

The first stage of the CLOs Measurement System has been improved by adding **dynamic language switching between Arabic and English** along with other user interface enhancements.

---

## ✨ الميزات الجديدة / New Features

### 1. 🌐 تبديل اللغة الديناميكي / Dynamic Language Switching

#### في النافذة الرئيسية / In Main Window:
- ✅ زر تبديل اللغة في الترويسة (Header)
- ✅ يعرض "🌐 EN" عند اللغة العربية و "🌐 عربي" عند اللغة الإنجليزية
- ✅ رسالة تأكيد قبل التبديل
- ✅ إعادة تشغيل النافذة تلقائياً بعد التبديل

#### في نافذة المرحلة الأولى / In Stage 1 Dialog:
- ✅ زر تبديل اللغة في الترويسة
- ✅ حفظ البيانات قبل التبديل (إذا كانت هناك تعديلات)
- ✅ إعادة بناء الواجهة كاملة بعد التبديل
- ✅ الحفاظ على جميع البيانات المدخلة

---

## 🔧 التحسينات التقنية / Technical Improvements

### 1. ملف `translations.py`
```python
# تحسين دالة الترجمة لدعم تمرير اللغة مباشرة
def t(key, language=None, fallback=None):
    """
    Args:
        key: مفتاح الترجمة
        language: اللغة (اختياري)
        fallback: القيمة البديلة
    """
```

**الفائدة:**
- يمكن الآن استخدام `t("key", "en")` بدون تغيير اللغة العامة
- مرونة أكبر في التعامل مع النصوص متعددة اللغات

### 2. ملف `views/main_window.py`

#### إضافات في `create_header()`:
```python
# زر تبديل اللغة
lang_btn = tk.Button(
    right_frame,
    text="🌐 EN" if get_language() == 'ar' else "🌐 عربي",
    ...
    command=self.toggle_language
)
```

#### تحسين دالة `toggle_language()`:
```python
def toggle_language(self):
    # تأكيد التبديل
    msg_ar = f"هل تريد تبديل اللغة..."
    msg_en = f"Do you want to switch language..."

    if messagebox.askyesno(...):
        set_language(new_lang)
        self.root.destroy()
        MainWindow(self.user, self.access_control).run()
```

### 3. ملف `dialogs/stage1_course_dialog.py`

#### إضافة ترويسة مع زر اللغة:
```python
# إطار الترويسة مع زر تبديل اللغة
header_frame = ttk.Frame(self)
header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

# العنوان
title_label = ttk.Label(
    header_frame,
    text=t("stage1_course_data", self.language),
    font=FONTS['arabic_header'] if self.language == 'ar' else FONTS['english_header']
)

# زر تبديل اللغة
lang_btn = ttk.Button(
    header_frame,
    text="🌐 EN" if self.language == 'ar' else "🌐 عربي",
    command=self.toggle_language
)
```

#### دالة تبديل اللغة الذكية:
```python
def toggle_language(self):
    # حفظ البيانات قبل التبديل (إذا كانت هناك تعديلات)
    if self.is_dirty:
        # رسالة تأكيد
        result = messagebox.askyesnocancel(...)
        if result:
            self.save_course()

    # تبديل اللغة
    self.language = 'en' if self.language == 'ar' else 'ar'

    # إعادة بناء الواجهة
    for widget in self.winfo_children():
        widget.destroy()
    self.setup_ui()
    self.load_data()
```

---

## 📊 الهيكل المحسن / Improved Structure

```
النافذة الرئيسية / Main Window
├── الترويسة / Header
│   ├── العنوان / Title
│   ├── زر تبديل اللغة / Language Toggle Button 🌐
│   └── زر تسجيل الخروج / Logout Button
│
└── نافذة المرحلة الأولى / Stage 1 Dialog
    ├── الترويسة / Header
    │   ├── العنوان / Title
    │   └── زر تبديل اللغة / Language Toggle Button 🌐
    │
    ├── التبويبات / Tabs
    │   ├── معلومات المقرر / Course Information
    │   ├── نواتج التعلم / Learning Outcomes
    │   ├── الموضوعات / Topics
    │   ├── أنشطة التقييم / Assessment Activities
    │   └── جدول المواصفات / Table of Specifications
    │
    └── أزرار التحكم / Control Buttons
        ├── حفظ / Save
        ├── إكمال المرحلة / Complete Stage
        ├── إلغاء / Cancel
        └── مساعدة / Help
```

---

## 🎯 الفوائد / Benefits

### 1. **تجربة مستخدم محسنة / Enhanced User Experience**
- تبديل سلس بين اللغتين دون فقدان البيانات
- واجهة موحدة بين النوافذ المختلفة
- رسائل واضحة باللغتين

### 2. **مرونة أكبر / Greater Flexibility**
- يمكن للمستخدمين اختيار اللغة المفضلة في أي وقت
- دعم المستخدمين متعددي اللغات
- سهولة الاستخدام للمستخدمين الدوليين

### 3. **قابلية الصيانة / Maintainability**
- كود نظيف ومنظم
- سهولة إضافة لغات جديدة مستقبلاً
- فصل واضح بين المنطق والعرض

---

## 📝 ملاحظات مهمة / Important Notes

### الحفاظ على البيانات / Data Preservation
- ✅ يتم حفظ البيانات تلقائياً قبل تبديل اللغة في نافذة المرحلة الأولى
- ✅ يُطلب من المستخدم تأكيد الحفظ إذا كانت هناك تعديلات غير محفوظة
- ✅ لا يتم فقدان أي بيانات أثناء عملية التبديل

### الأداء / Performance
- إعادة بناء الواجهة سريعة وفعالة
- لا توجد تأخيرات ملحوظة
- استخدام ذاكرة محسّن

### التوافقية / Compatibility
- ✅ متوافق مع جميع أنظمة التشغيل (Windows, macOS, Linux)
- ✅ يعمل مع Python 3.7+
- ✅ متوافق مع Tkinter 8.6+

---

## 🚀 كيفية الاستخدام / How to Use

### تبديل اللغة في النافذة الرئيسية:
1. انقر على زر "🌐 EN" أو "🌐 عربي" في الترويسة
2. أكد اختيارك في نافذة التأكيد
3. ستتم إعادة تشغيل النافذة باللغة الجديدة

### تبديل اللغة في نافذة المرحلة الأولى:
1. انقر على زر "🌐 EN" أو "🌐 عربي" في أعلى النافذة
2. إذا كانت هناك تعديلات غير محفوظة، سيُطلب منك حفظها
3. ستتم إعادة بناء الواجهة باللغة الجديدة مع الحفاظ على جميع البيانات

---

## 🔮 التحسينات المستقبلية المقترحة / Suggested Future Improvements

### قصيرة المدى / Short-term:
1. ✨ إضافة اختصار لوحة مفاتيح لتبديل اللغة (Ctrl+L)
2. ✨ حفظ تفضيل اللغة في ملف إعدادات المستخدم
3. ✨ إضافة رسوم متحركة سلسة عند التبديل

### متوسطة المدى / Medium-term:
1. 🌍 دعم لغات إضافية (فرنسي، إسباني، إلخ)
2. 📱 واجهة متجاوبة تدعم الشاشات المختلفة
3. 🎨 ثيمات قابلة للتخصيص

### طويلة المدى / Long-term:
1. ☁️ مزامنة تفضيلات اللغة عبر الأجهزة
2. 🤖 ترجمة تلقائية باستخدام AI
3. 🗣️ دعم الأوامر الصوتية

---

## 📚 المراجع / References

- [Documentation - Tkinter](https://docs.python.org/3/library/tkinter.html)
- [Table of Specifications Guide](./docs/TABLE_OF_SPECIFICATIONS.md)
- [Stage 1 Development Documentation](./docs/STAGE1_DEVELOPMENT_DOCUMENTATION.md)

---

## 👥 المساهمون / Contributors

- **د. حسين يوسف عبد العظيم** - تطوير وتصميم النظام
- **قسم الإحصاء - جامعة تبوك** - الدعم الفني والإشراف

---

## 📞 الدعم الفني / Technical Support

للحصول على المساعدة أو الإبلاغ عن مشاكل:
- 📧 Email: h.abdulazim@ut.edu.sa
- 🏛️ Department of Statistics, University of Tabuk

---

**آخر تحديث / Last Updated:** 2025-12-25
**الحالة / Status:** ✅ مكتمل ومختبر / Complete and Tested

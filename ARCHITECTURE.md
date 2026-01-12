# بنية تطبيق Streamlit / Streamlit Application Architecture

## 📐 نظرة عامة / Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  نظام قياس مخرجات التعلم                   │
│            CLOs Measurement System (Web)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │       Streamlit Frontend            │
        │   (streamlit_app.py)                │
        │   - تسجيل الدخول / Login            │
        │   - لوحة التحكم / Dashboard          │
        │   - القوائم الديناميكية / Menus     │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │      Business Logic Layer           │
        │   - Session Management              │
        │   - Authentication                  │
        │   - Role-based Access               │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │         Data Access Layer           │
        │   models/database.py                │
        │   - CRUD Operations                 │
        │   - Query Building                  │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │       Database (SQLite)             │
        │   clos_system.db                    │
        │   - Users, Programs, Courses        │
        │   - CLOs, Sections, Grades          │
        └─────────────────────────────────────┘
```

---

## 🔐 نظام المصادقة / Authentication System

```
┌──────────────┐
│  User Input  │
│  Username    │
│  Password    │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ authenticate()   │
│ - Hash Compare   │
│ - Role Check     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐     ┌──────────────────┐
│  Success?        │────►│ Session State    │
│                  │  Y  │ - user           │
└──────┬───────────┘     │ - authenticated  │
       │ N               │ - language       │
       ▼                 └──────────────────┘
┌──────────────────┐
│  Error Message   │
└──────────────────┘
```

---

## 👥 نظام الصلاحيات / Role-based Access Control

### Admin (مدير النظام)
```
┌─────────────────────────────────┐
│  🏠 Dashboard                    │
│  👥 Users Management             │
│  🏛️ Programs Management          │
│  📚 Courses Management           │
│  📊 Reports                      │
│  ⚙️ Settings                     │
└─────────────────────────────────┘
```

### Program Coordinator (منسق برنامج)
```
┌─────────────────────────────────┐
│  🏠 Dashboard                    │
│  🏛️ My Programs                  │
│  📚 Courses Management           │
│  📊 Reports                      │
└─────────────────────────────────┘
```

### Course Coordinator (منسق مقرر)
```
┌─────────────────────────────────┐
│  🏠 Dashboard                    │
│  📚 My Courses                   │
│  📝 Assessment                   │
│  📊 My Reports                   │
└─────────────────────────────────┘
```

### Section Instructor (مدرس شعبة)
```
┌─────────────────────────────────┐
│  🏠 Dashboard                    │
│  📚 My Sections                  │
│  📝 Enter Grades                 │
│  📊 Section Reports              │
└─────────────────────────────────┘
```

---

## 🔄 دورة حياة الطلب / Request Lifecycle

```
1. User Action (Login, Click, Input)
        │
        ▼
2. Streamlit Event Handler
        │
        ▼
3. Session State Update
        │
        ▼
4. Database Query (if needed)
        │
        ▼
5. UI Re-render (st.rerun())
        │
        ▼
6. Display Updated Content
```

---

## 📦 الوحدات المستخدمة / Used Components

### Frontend (Streamlit)
```python
streamlit_app.py
├── init_session_state()     # تهيئة الجلسة
├── login_page()              # صفحة تسجيل الدخول
├── main_app()                # التطبيق الرئيسي
└── show_dashboard()          # لوحة التحكم
```

### Backend (Python Models)
```python
models/
├── database.py               # قاعدة البيانات
├── user.py                   # نموذج المستخدم
├── program.py                # نموذج البرنامج
├── course.py                 # نموذج المقرر
├── clo.py                    # نموذج مخرج التعلم
└── section.py                # نموذج الشعبة
```

### Utilities
```python
utils/
├── translations.py           # الترجمات
├── validators.py             # التحقق من البيانات
└── excel_template_utils.py   # قوالب Excel
```

---

## 🎨 نظام التصميم / Design System

### Colors (الألوان)
```css
Primary Color:    #1f77b4  (أزرق)
Secondary Color:  #f0f2f6  (رمادي فاتح)
Success:          #4CAF50  (أخضر)
Warning:          #ffa500  (برتقالي)
Danger:           #ff4b4b  (أحمر)
```

### Typography (الخطوط)
```css
Font Family: 'Cairo', sans-serif
Heading: 600-700 weight
Body: 400 weight
Small: 300 weight
```

### RTL Support (دعم العربية)
```css
.rtl {
    direction: rtl;
    text-align: right;
}

.ltr {
    direction: ltr;
    text-align: left;
}
```

---

## 💾 نموذج البيانات / Data Model

```
User (المستخدم)
├── id
├── username
├── password_hash
├── full_name
├── email
├── role (Admin, Coordinator, Instructor)
└── department

Program (البرنامج)
├── id
├── code
├── name_ar
├── name_en
└── coordinator_id

Course (المقرر)
├── id
├── code
├── name_ar
├── name_en
├── program_id
└── coordinator_id

CLO (مخرج التعلم)
├── id
├── code
├── description
├── category (Knowledge, Skills, Values)
├── course_id
└── aligned_plos

Section (الشعبة)
├── id
├── section_number
├── course_id
├── instructor_id
└── semester
```

---

## 🔌 التكامل المستقبلي / Future Integrations

### المخطط:
1. **API REST** لتطبيقات الموبايل
2. **WebSocket** للتحديثات الفورية
3. **OAuth2** لتسجيل دخول خارجي
4. **Export to PDF/Excel** من التقارير
5. **Email Notifications** للإشعارات
6. **Analytics Dashboard** للإحصائيات المتقدمة

---

## 📊 مسار البيانات / Data Flow

### إنشاء مقرر جديد:
```
User Input (Form)
    ↓
Validation (Python)
    ↓
Create Course Object
    ↓
Save to Database (SQLite)
    ↓
Update Session State
    ↓
Refresh UI (st.rerun())
    ↓
Show Success Message
```

### إدخال درجات:
```
Select Section
    ↓
Load Students List
    ↓
Input Grades (Table)
    ↓
Calculate Statistics
    ↓
Save to Database
    ↓
Generate Report
    ↓
Display Results
```

---

## 🚀 الأداء / Performance

### Caching Strategy:
```python
@st.cache_resource  # للموارد الثقيلة (Database Connection)
@st.cache_data      # للبيانات الثابتة (Translations, Programs)
```

### Session State:
```python
st.session_state.user          # بيانات المستخدم
st.session_state.language      # اللغة المختارة
st.session_state.authenticated # حالة تسجيل الدخول
```

---

## 🔒 الأمان / Security

### مستويات الأمان:
1. **Password Hashing**: bcrypt/SHA256
2. **CSRF Protection**: Streamlit built-in
3. **SQL Injection**: Parameterized queries
4. **XSS Prevention**: Streamlit auto-escape
5. **Role Validation**: Before each action

---

## 📝 الخطوات القادمة / Next Steps

### المرحلة 1: الوظائف الأساسية
- [ ] إدارة المستخدمين الكاملة
- [ ] إدارة البرامج والمقررات
- [ ] نظام إدخال الدرجات

### المرحلة 2: التقييم والتقارير
- [ ] تحليل مخرجات التعلم
- [ ] توليد التقارير التلقائية
- [ ] الرسوم البيانية والإحصائيات

### المرحلة 3: التحسينات
- [ ] تصدير/استيراد Excel
- [ ] نظام الإشعارات
- [ ] التكامل مع أنظمة خارجية

---

**آخر تحديث:** 2026-01-11
**الإصدار:** 2.0 (Streamlit Web)

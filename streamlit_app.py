"""
نظام قياس مخرجات التعلم - Streamlit Web Application
Academic Programs and Course Learning Outcomes Measurement System
"""

import streamlit as st
import sys
import os
from pathlib import Path

# إضافة المجلد الحالي إلى المسار
sys.path.insert(0, str(Path(__file__).parent))

# استيراد النماذج والوظائف الموجودة
from models.database import Database, User, UserRole
from translations import t
from pages.users_management import show_users_management
from pages.programs_management import show_programs_management
from pages.courses_management import show_courses_management

# إعداد الصفحة
st.set_page_config(
    page_title="نظام قياس مخرجات التعلم",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تطبيق CSS مخصص للدعم الكامل للعربية
st.markdown("""
<style>
    /* دعم النص العربي */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');

    * {
        font-family: 'Cairo', sans-serif !important;
    }

    /* RTL Support */
    .rtl {
        direction: rtl;
        text-align: right;
    }

    .ltr {
        direction: ltr;
        text-align: left;
    }

    /* تحسين العناوين */
    h1, h2, h3 {
        color: #1f77b4;
        font-weight: 600;
    }

    /* تحسين الأزرار */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        padding: 10px 20px;
    }

    /* تحسين الإدخالات */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        font-size: 16px;
    }

    /* تحسين الـ Sidebar */
    .css-1d391kg {
        background-color: #f0f2f6;
    }

    /* تحسين البطاقات */
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }

    /* ألوان الأدوار */
    .role-admin {
        background-color: #ff4b4b;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
    }

    .role-program_coordinator {
        background-color: #ffa500;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
    }

    .role-course_coordinator {
        background-color: #4CAF50;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
    }

    .role-section_instructor {
        background-color: #2196F3;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
    }

    /* تحسين القائمة الجانبية */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }

    /* تحسين أزرار الراديو في القائمة */
    [data-testid="stSidebar"] .row-widget.stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 3px;
        overflow-y: visible;
        max-height: none;
    }

    [data-testid="stSidebar"] .row-widget.stRadio > div label {
        background-color: white;
        padding: 8px 12px;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        transition: all 0.2s;
        cursor: pointer;
        display: flex;
        align-items: center;
        font-size: 14px;
        font-weight: 500;
        min-height: 40px;
    }

    [data-testid="stSidebar"] .row-widget.stRadio > div label:hover {
        border-color: #1f77b4;
        background-color: #e3f2fd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* العنصر المحدد */
    [data-testid="stSidebar"] .row-widget.stRadio > div label[data-selected="true"] {
        background-color: #1f77b4;
        color: white;
        border-color: #1f77b4;
        font-weight: 600;
    }

    /* إخفاء دائرة الراديو */
    [data-testid="stSidebar"] .row-widget.stRadio > div label > div:first-child {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# تهيئة قاعدة البيانات
@st.cache_resource
def init_database():
    """تهيئة قاعدة البيانات"""
    db_path = Path(__file__).parent / 'clos_system.db'
    db = Database(str(db_path))
    return db

# تهيئة Session State
def init_session_state():
    """تهيئة حالة الجلسة"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'language' not in st.session_state:
        st.session_state.language = 'ar'
    if 'db' not in st.session_state:
        st.session_state.db = init_database()

def login_page():
    """صفحة تسجيل الدخول"""
    lang = st.session_state.language
    is_rtl = lang == 'ar'

    # عنوان النظام
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="{'rtl' if is_rtl else 'ltr'}" style="text-align: center;">
            <h1>🎓 {t('app_title', lang)}</h1>
            <p style="color: #666; font-size: 18px;">{t('app_subtitle', lang)}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # نموذج تسجيل الدخول
        with st.container():
            st.markdown(f"""
            <div class="card {'rtl' if is_rtl else 'ltr'}">
                <h2 style="text-align: center;">{t('login', lang)}</h2>
            </div>
            """, unsafe_allow_html=True)

            # اختيار اللغة
            language_option = st.selectbox(
                "🌐 Language / اللغة",
                options=['العربية', 'English'],
                index=0 if lang == 'ar' else 1,
                key='language_select'
            )

            if language_option == 'العربية' and lang != 'ar':
                st.session_state.language = 'ar'
                st.rerun()
            elif language_option == 'English' and lang != 'en':
                st.session_state.language = 'en'
                st.rerun()

            # حقول تسجيل الدخول
            username = st.text_input(
                f"👤 {t('username', lang)}",
                key='username_input',
                placeholder=t('enter_username', lang)
            )

            password = st.text_input(
                f"🔒 {t('password', lang)}",
                type='password',
                key='password_input',
                placeholder=t('enter_password', lang)
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # زر تسجيل الدخول
            if st.button(f"🚀 {t('login', lang)}", use_container_width=True, type='primary'):
                if username and password:
                    # محاولة تسجيل الدخول
                    db = st.session_state.db
                    user = db.authenticate_user(username, password)

                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.success(f"✅ {t('login_success', lang)}")
                        st.rerun()
                    else:
                        st.error(f"❌ {t('login_failed', lang)}")
                else:
                    st.warning(f"⚠️ {t('please_fill_all_fields', lang)}")

        # معلومات المطور
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align: center; color: #999; font-size: 14px;">
            <p>{t('developed_by', lang)} | Version 2.0 (Streamlit)</p>
        </div>
        """, unsafe_allow_html=True)

def main_app():
    """التطبيق الرئيسي بعد تسجيل الدخول"""
    user = st.session_state.user
    lang = st.session_state.language
    is_rtl = lang == 'ar'

    # Sidebar - القائمة الجانبية
    with st.sidebar:
        st.markdown(f"""
        <div class="{'rtl' if is_rtl else 'ltr'}" style="text-align: center;">
            <h3>👤 {t('welcome', lang)}</h3>
            <p style="font-size: 16px; font-weight: 600;">{user.full_name}</p>
            <p class="role-{user.role.value.lower()}" style="display: inline-block;">{t(user.role.value.lower(), lang)}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # القوائم حسب الصلاحيات
        st.markdown(f"### 📋 {t('main_menu', lang)}")
        st.markdown("")  # مسافة صغيرة

        menu_items = []

        if user.role == UserRole.ADMIN:
            menu_items = [
                ("🏠", "dashboard", t("dashboard", lang)),
                ("👥", "users", t("users_management", lang)),
                ("🏛️", "programs", t("programs_management", lang)),
                ("📚", "courses", t("courses_management", lang)),
                ("📊", "reports", t("reports", lang)),
                ("⚙️", "settings", t("settings", lang)),
            ]
        elif user.role == UserRole.PROGRAM_COORDINATOR:
            menu_items = [
                ("🏠", "dashboard", t("dashboard", lang)),
                ("🏛️", "programs", t("my_programs", lang)),
                ("📚", "courses", t("courses_management", lang)),
                ("📊", "reports", t("reports", lang)),
            ]
        elif user.role == UserRole.COURSE_COORDINATOR:
            menu_items = [
                ("🏠", "dashboard", t("dashboard", lang)),
                ("📚", "my_courses", t("my_courses", lang)),
                ("📝", "assessment", t("assessment", lang)),
                ("📊", "reports", t("my_reports", lang)),
            ]
        else:  # SECTION_INSTRUCTOR
            menu_items = [
                ("🏠", "dashboard", t("dashboard", lang)),
                ("📚", "sections", t("my_sections", lang)),
                ("📝", "grades", t("enter_grades", lang)),
                ("📊", "reports", t("section_reports", lang)),
            ]

        # عرض القائمة
        selected_page = st.radio(
            "",
            options=[item[1] for item in menu_items],
            format_func=lambda x: next((f"{item[0]} {item[2]}" for item in menu_items if item[1] == x), x),
            key='menu_selection',
            label_visibility="collapsed"
        )

        st.markdown("---")

        # زر تغيير اللغة
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🌐 {t('change_language', lang)}", use_container_width=True):
                st.session_state.language = 'en' if lang == 'ar' else 'ar'
                st.rerun()

        # زر تسجيل الخروج
        with col2:
            if st.button(f"🚪 {t('logout', lang)}", use_container_width=True, type='primary'):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()

    # المحتوى الرئيسي
    st.markdown(f"<div class='{'rtl' if is_rtl else 'ltr'}'>", unsafe_allow_html=True)

    if selected_page == 'dashboard':
        show_dashboard(user, lang)
    elif selected_page == 'users':
        show_users_management(st.session_state.db, user, lang)
    elif selected_page == 'programs':
        show_programs_management(st.session_state.db, user, lang)
    elif selected_page == 'courses' or selected_page == 'my_courses':
        show_courses_management(st.session_state.db, user, lang)
    elif selected_page == 'sections':
        st.title(f"📚 {t('my_sections', lang)}")
        st.info(f"🚧 {t('under_development', lang)}")
    elif selected_page == 'reports' or selected_page == 'my_reports' or selected_page == 'section_reports':
        st.title(f"📊 {t('reports', lang)}")
        st.info(f"🚧 {t('under_development', lang)}")
    elif selected_page == 'assessment':
        st.title(f"📝 {t('assessment', lang)}")
        st.info(f"🚧 {t('under_development', lang)}")
    elif selected_page == 'grades':
        st.title(f"📝 {t('enter_grades', lang)}")
        st.info(f"🚧 {t('under_development', lang)}")
    elif selected_page == 'settings':
        st.title(f"⚙️ {t('settings', lang)}")
        st.info(f"🚧 {t('under_development', lang)}")

    st.markdown("</div>", unsafe_allow_html=True)

def show_dashboard(user: User, lang: str):
    """عرض لوحة المعلومات"""
    is_rtl = lang == 'ar'
    db = st.session_state.db

    st.title(f"🏠 {t('dashboard', lang)}")

    # جمع الإحصائيات
    programs_count = len(db.get_all_programs())
    courses_count = len(db.get_all_courses())
    users_count = len(db.get_all_users())

    # حساب البرامج النشطة
    active_programs = len([p for p in db.get_all_programs() if p.get('is_active', True)])

    # حساب المقررات النشطة
    active_courses = len([c for c in db.get_all_courses() if c.get('is_active', True)])

    # بطاقات الإحصائيات
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <h2 style="color: white;">📚</h2>
            <h3 style="color: white;">{courses_count}</h3>
            <p style="color: white; font-size: 16px;">{t('courses', lang) if lang == 'ar' else 'Courses'}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
            <h2 style="color: white;">🏛️</h2>
            <h3 style="color: white;">{programs_count}</h3>
            <p style="color: white; font-size: 16px;">{t('programs', lang) if lang == 'ar' else 'Programs'}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white;">
            <h2 style="color: white;">👥</h2>
            <h3 style="color: white;">{users_count}</h3>
            <p style="color: white; font-size: 16px;">{t('users', lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        # حساب نسبة الإنجاز (المقررات النشطة / إجمالي المقررات)
        completion_rate = int((active_courses / courses_count * 100)) if courses_count > 0 else 0
        st.markdown(f"""
        <div class="card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white;">
            <h2 style="color: white;">✅</h2>
            <h3 style="color: white;">{completion_rate}%</h3>
            <p style="color: white; font-size: 16px;">{t('active_courses', lang) if lang == 'ar' else 'Active'}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # تفاصيل إضافية
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="card {'rtl' if is_rtl else 'ltr'}">
            <h3>📋 {t('user_info', lang)}</h3>
            <p><strong>{t('full_name', lang)}:</strong> {user.full_name}</p>
            <p><strong>{t('username', lang)}:</strong> {user.username}</p>
            <p><strong>{t('email', lang)}:</strong> {user.email}</p>
            <p><strong>{t('role', lang)}:</strong> {t(user.role.value.lower(), lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card {'rtl' if is_rtl else 'ltr'}">
            <h3>📊 {t('quick_stats', lang)}</h3>
            <p><strong>{t('active_programs', lang)}:</strong> {active_programs} / {programs_count}</p>
            <p><strong>{t('active_courses', lang)}:</strong> {active_courses} / {courses_count}</p>
            <p><strong>{t('total_users', lang)}:</strong> {users_count}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # عرض آخر البرامج والمقررات
    if user.role in [UserRole.ADMIN, UserRole.PROGRAM_COORDINATOR]:
        st.subheader(f"📌 {t('recent_activity', lang)}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{t('recent_programs', lang)}**")
            programs = db.get_all_programs()
            if programs:
                # عرض آخر 3 برامج
                for program in programs[-3:]:
                    program_name = program.get('program_name_ar' if lang == 'ar' else 'program_name_en', '')
                    status = '🟢' if program.get('is_active', True) else '🔴'
                    st.write(f"{status} {program.get('program_code', '')} - {program_name}")
            else:
                st.info(t('no_programs_yet', lang))

        with col2:
            st.markdown(f"**{t('recent_courses', lang)}**")
            courses = db.get_all_courses()
            if courses:
                # عرض آخر 3 مقررات
                for course in courses[-3:]:
                    course_name = course.get('course_title_ar' if lang == 'ar' else 'course_title_en', '')
                    status = '🟢' if course.get('is_active', True) else '🔴'
                    st.write(f"{status} {course.get('course_code', '')} - {course_name}")
            else:
                st.info(t('no_courses_yet', lang))

# البرنامج الرئيسي
def main():
    """نقطة البداية للتطبيق"""
    init_session_state()

    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()

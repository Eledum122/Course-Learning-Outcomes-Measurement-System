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
# تم إزالة الاستيراد من هنا لتجنب مشاكل الـ cache
# سيتم استيراد الصفحات ديناميكياً عند الحاجة

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
            col_login, col_clear = st.columns([3, 1])

            with col_login:
                login_clicked = st.button(f"🚀 {t('login', lang)}", use_container_width=True, type='primary')

            with col_clear:
                clear_clicked = st.button("🔄", use_container_width=True, help="مسح الجلسة / Clear Session")

            if clear_clicked:
                # مسح جميع بيانات الجلسة بالكامل
                st.cache_data.clear()
                st.cache_resource.clear()
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("✅ تم مسح الجلسة بالكامل! يرجى تحديث الصفحة / Session completely cleared! Please refresh the page.")
                st.info("اضغط Ctrl+Shift+R لتحديث كامل / Press Ctrl+Shift+R for full refresh")
                st.stop()

            if login_clicked:
                if username and password:
                    # مسح أي جلسة قديمة
                    if 'authenticated' in st.session_state:
                        del st.session_state['authenticated']
                    if 'user' in st.session_state:
                        del st.session_state['user']

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
    db = st.session_state.db

    # إعادة بناء كائن المستخدم دائماً من قاعدة البيانات لضمان صحة الأدوار
    users = db.load_users()
    username = st.session_state.user.username if st.session_state.user else None

    if username:
        for u_data in users:
            if u_data.get('username') == username:
                from models.database import User as DBUser
                user = DBUser(
                    user_id=u_data.get('user_id', ''),
                    username=u_data.get('username', ''),
                    password_hash=u_data.get('password_hash', ''),
                    full_name=u_data.get('full_name', ''),
                    email=u_data.get('email', ''),
                    roles=u_data.get('roles', []),
                    employee_id=u_data.get('employee_id', ''),
                    faculty_id=u_data.get('faculty_id', '')
                )
                st.session_state.user = user
                break

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
                # المجموعة 1: الإعدادات والإدارة (أزرق)
                ("🔷🔷🔷", "sep1", "الإعدادات والإدارة 🔷🔷🔷"),
                ("🏠", "dashboard", t("dashboard", lang)),
                ("⚙️", "settings", t("settings", lang)),
                ("👥", "users", t("users_management", lang)),
                ("👨‍🏫", "faculty", "أعضاء هيئة التدريس / Faculty"),
                ("🏛️", "programs", t("programs_management", lang)),
                # المجموعة 2: المرحلة 1 - معلومات المقررات (أخضر)
                ("🟩🟩🟩", "sep2", "المرحلة 1: معلومات المقررات 🟩🟩🟩"),
                ("📚", "courses", t("courses_management", lang)),
                ("🏫", "external_teaching", "التدريس الخارجي / External Teaching"),
                ("📝", "clos", "مخرجات التعلم / CLOs"),
                ("📑", "course_topics", "موضوعات المقرر / Course Topics"),
                ("📊", "assessment_activities", "أنشطة التقييم / Assessment"),
                # المجموعة 3: المرحلة 2 - قياس المخرجات (بنفسجي)
                ("🟪🟪🟪", "sep3", "المرحلة 2: قياس المخرجات 🟪🟪🟪"),
                ("📊", "stage2_clo_marks", "درجات CLOs"),
                ("🔗", "stage2_topics_clos", "ربط الموضوعات بـ CLOs"),
                ("📝", "stage2_topics_activities", "ربط الموضوعات بالأنشطة"),
                ("📊", "stage2_clos_activities", "المخرجات والأنشطة"),
                ("📋", "stage2_specs_table", "جدول المواصفات"),
                # المجموعة 4: المرحلة 3 - إعدادات الفصول والشعب (برتقالي)
                ("🟧🟧🟧", "sep4", "المرحلة 3: الفصول والشعب 🟧🟧🟧"),
                ("🎯", "clo_semester_settings", "إعدادات الفصل"),
                ("📖", "sections_mgmt", "الشعب الدراسية / Sections"),
                # المجموعة 5: المرحلة 4 - الطلاب والدرجات (أحمر)
                ("🟥🟥🟥", "sep5", "المرحلة 4: الطلاب والدرجات 🟥🟥🟥"),
                ("👥", "section_students", "طلاب الشعبة / Students"),
                ("📝", "student_grades", "درجات الشعبة / Grades"),
                # المجموعة 6: المرحلة 5 - التقارير ولوحات البيانات (أصفر)
                ("🟨🟨🟨", "sep6", "المرحلة 5: التقارير 🟨🟨🟨"),
                ("📊", "clo_report", "تقرير قياس المخرجات / CLO Report"),
                ("📈", "aggregated_clo_report", "التقرير المجمع / Collected Report"),
                ("📊", "grades_dashboard", "لوحة بيانات الدرجات / Grades Dashboard"),
                ("📊", "collected_grades_dashboard", "الدرجات المجمعة / Collected Grades"),
                ("📝", "activity_sheet_report", "ورقة النشاط / Activity Sheet"),
                ("📋", "section_progress_report", "متابعة الشعب / Section Progress"),
                ("📈", "reports", t("reports", lang)),
            ]
        elif user.role == UserRole.PROGRAM_COORDINATOR:
            menu_items = [
                # المجموعة 1: الإدارة (أزرق)
                ("🔷🔷🔷", "sep1", "الإدارة 🔷🔷🔷"),
                ("🏠", "dashboard", t("dashboard", lang)),
                ("🏛️", "programs", t("my_programs", lang)),
                # المجموعة 2: المرحلة 1 - معلومات المقررات (أخضر)
                ("🟩🟩🟩", "sep2", "المرحلة 1: معلومات المقررات 🟩🟩🟩"),
                ("📚", "courses", t("courses_management", lang)),
                ("🏫", "external_teaching", "التدريس الخارجي / External Teaching"),
                ("📝", "clos", "مخرجات التعلم / CLOs"),
                ("📑", "course_topics", "موضوعات المقرر / Course Topics"),
                ("📊", "assessment_activities", "أنشطة التقييم / Assessment"),
                # المجموعة 3: المرحلة 2 - قياس المخرجات (بنفسجي)
                ("🟪🟪🟪", "sep3", "المرحلة 2: قياس المخرجات 🟪🟪🟪"),
                ("📊", "stage2_clo_marks", "درجات CLOs"),
                ("🔗", "stage2_topics_clos", "ربط الموضوعات بـ CLOs"),
                ("📝", "stage2_topics_activities", "ربط الموضوعات بالأنشطة"),
                ("📊", "stage2_clos_activities", "المخرجات والأنشطة"),
                ("📋", "stage2_specs_table", "جدول المواصفات"),
                # المجموعة 4: المرحلة 3 - إعدادات الفصول والشعب (برتقالي)
                ("🟧🟧🟧", "sep4", "المرحلة 3: الفصول والشعب 🟧🟧🟧"),
                ("🎯", "clo_semester_settings", "إعدادات الفصل"),
                ("📖", "sections_mgmt", "الشعب الدراسية / Sections"),
                # المجموعة 5: المرحلة 4 - الطلاب والدرجات (أحمر)
                ("🟥🟥🟥", "sep5", "المرحلة 4: الطلاب والدرجات 🟥🟥🟥"),
                ("👥", "section_students", "طلاب الشعبة / Students"),
                ("📝", "student_grades", "درجات الطلاب / Grades"),
                # المجموعة 6: المرحلة 5 - التقارير (أصفر)
                ("🟨🟨🟨", "sep6", "المرحلة 5: التقارير 🟨🟨🟨"),
                ("📊", "clo_report", "تقرير قياس المخرجات / CLO Report"),
                ("📈", "aggregated_clo_report", "التقرير المجمع / Collected Report"),
                ("📊", "grades_dashboard", "لوحة بيانات الدرجات / Grades Dashboard"),
                ("📊", "collected_grades_dashboard", "الدرجات المجمعة / Collected Grades"),
                ("📝", "activity_sheet_report", "ورقة النشاط / Activity Sheet"),
                ("📋", "section_progress_report", "متابعة الشعب / Section Progress"),
                ("📈", "reports", t("reports", lang)),
            ]
        elif user.role == UserRole.COURSE_COORDINATOR:
            menu_items = [
                # المجموعة 1: الإدارة (أزرق)
                ("🔷🔷🔷", "sep1", "الإدارة 🔷🔷🔷"),
                ("🏠", "dashboard", t("dashboard", lang)),
                ("📚", "my_courses", t("my_courses", lang)),
                # المجموعة 2: المرحلة 1 - معلومات المقررات (أخضر)
                ("🟩🟩🟩", "sep2", "المرحلة 1: معلومات المقررات 🟩🟩🟩"),
                ("📝", "clos", "مخرجات التعلم / CLOs"),
                ("📑", "course_topics", "موضوعات المقرر / Course Topics"),
                ("📊", "assessment_activities", "أنشطة التقييم / Assessment"),
                # المجموعة 3: المرحلة 2 - قياس المخرجات (بنفسجي)
                ("🟪🟪🟪", "sep3", "المرحلة 2: قياس المخرجات 🟪🟪🟪"),
                ("📊", "stage2_clo_marks", "درجات CLOs"),
                ("🔗", "stage2_topics_clos", "ربط الموضوعات بـ CLOs"),
                ("📝", "stage2_topics_activities", "ربط الموضوعات بالأنشطة"),
                ("📊", "stage2_clos_activities", "المخرجات والأنشطة"),
                ("📋", "stage2_specs_table", "جدول المواصفات"),
                # المجموعة 4: المرحلة 3 - إعدادات الفصول والشعب (برتقالي)
                ("🟧🟧🟧", "sep4", "المرحلة 3: الفصول والشعب 🟧🟧🟧"),
                ("🎯", "clo_semester_settings", "إعدادات الفصل"),
                ("📖", "sections_mgmt", "الشعب الدراسية / Sections"),
                # المجموعة 5: المرحلة 4 - الطلاب والدرجات (أحمر)
                ("🟥🟥🟥", "sep5", "المرحلة 4: الطلاب والدرجات 🟥🟥🟥"),
                ("👥", "section_students", "طلاب الشعبة / Students"),
                ("📝", "student_grades", "درجات الطلاب / Grades"),
                # المجموعة 6: المرحلة 5 - التقارير (أصفر)
                ("🟨🟨🟨", "sep6", "المرحلة 5: التقارير 🟨🟨🟨"),
                ("📊", "clo_report", "تقرير قياس المخرجات / CLO Report"),
                ("📈", "aggregated_clo_report", "التقرير المجمع / Collected Report"),
                ("📊", "grades_dashboard", "لوحة بيانات الدرجات / Grades Dashboard"),
                ("📊", "collected_grades_dashboard", "الدرجات المجمعة / Collected Grades"),
                ("📝", "activity_sheet_report", "ورقة النشاط / Activity Sheet"),
                ("📋", "section_progress_report", "متابعة الشعب / Section Progress"),
            ]
        else:  # SECTION_INSTRUCTOR
            menu_items = [
                # المجموعة 1: الإدارة (أزرق)
                ("🔷🔷🔷", "sep1", "الإدارة 🔷🔷🔷"),
                ("🏠", "dashboard", t("dashboard", lang)),
                ("📚", "sections", t("my_sections", lang)),
                # المجموعة 2: الطلاب والدرجات (أحمر)
                ("🟥🟥🟥", "sep2", "الطلاب والدرجات 🟥🟥🟥"),
                ("👥", "section_students", "طلاب الشعبة / Section Students"),
                ("📝", "grades", t("enter_grades", lang)),
                # المجموعة 3: التقارير (أصفر)
                ("🟨🟨🟨", "sep3", "التقارير 🟨🟨🟨"),
                ("📊", "grades_dashboard", "لوحة بيانات الدرجات / Grades Dashboard"),
                ("📊", "clo_report", "تقرير قياس المخرجات / CLO Report"),
                ("📝", "activity_sheet_report", "ورقة النشاط / Activity Sheet"),
                ("📈", "reports", t("section_reports", lang)),
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
        show_dashboard(st.session_state.user, lang)
    elif selected_page == 'users':
        # استيراد ديناميكي لتجنب مشاكل الـ cache
        import importlib
        from pages import users_management
        importlib.reload(users_management)
        users_management.show_users_management(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'faculty':
        # صفحة إدارة أعضاء هيئة التدريس
        import importlib
        from pages import faculty_management
        importlib.reload(faculty_management)
        faculty_management.show_faculty_management(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'programs':
        # استيراد ديناميكي لتجنب مشاكل الـ cache
        import importlib
        from pages import programs_management
        importlib.reload(programs_management)
        programs_management.show_programs_management(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'courses' or selected_page == 'my_courses':
        # استيراد ديناميكي لتجنب مشاكل الـ cache
        import importlib
        from pages import courses_management
        importlib.reload(courses_management)
        courses_management.show_courses_management(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'clos':
        # استيراد ديناميكي لصفحة CLOs
        import importlib
        from pages import clos_management
        importlib.reload(clos_management)
        clos_management.show_clos_management(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'course_topics':
        # استيراد ديناميكي لصفحة موضوعات المقرر
        import importlib
        from pages import course_topics
        importlib.reload(course_topics)
        course_topics.show_course_topics(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'assessment_activities':
        # استيراد ديناميكي لصفحة أنشطة التقييم
        import importlib
        from pages import assessment_activities
        importlib.reload(assessment_activities)
        assessment_activities.show_assessment_activities(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'sections':
        # صفحة شعبي للمدرس - توجيه لصفحة إدارة الشعب مع فلترة تلقائية
        import importlib
        from pages import sections_management
        importlib.reload(sections_management)
        sections_management.show_sections_management(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'sections_mgmt':
        # صفحة إدارة الشعب الدراسية
        import importlib
        from pages import sections_management
        importlib.reload(sections_management)
        sections_management.show_sections_management(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'section_students':
        # صفحة إدارة طلاب الشعبة
        import importlib
        from pages import section_students
        importlib.reload(section_students)
        section_students.show_section_students(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'student_grades':
        # صفحة إدخال درجات الطلاب
        import importlib
        from pages import student_grades
        importlib.reload(student_grades)
        student_grades.show_student_grades(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'grades_dashboard':
        # صفحة لوحة بيانات الدرجات
        import importlib
        from pages import grades_dashboard
        importlib.reload(grades_dashboard)
        grades_dashboard.show_grades_dashboard(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'collected_grades_dashboard':
        # صفحة لوحة بيانات الدرجات المجمعة
        import importlib
        from pages import collected_grades_dashboard
        importlib.reload(collected_grades_dashboard)
        collected_grades_dashboard.show_collected_grades_dashboard(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'external_teaching':
        # صفحة التدريس الخارجي
        import importlib
        from pages import external_teaching
        importlib.reload(external_teaching)
        external_teaching.show_external_teaching(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'clo_report':
        # صفحة تقرير قياس المخرجات
        import importlib
        from pages import clo_assessment_report
        importlib.reload(clo_assessment_report)
        clo_assessment_report.show_clo_assessment_report(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'aggregated_clo_report':
        # صفحة التقرير المجمع لقياس المخرجات
        import importlib
        from pages import aggregated_clo_report
        importlib.reload(aggregated_clo_report)
        aggregated_clo_report.show_aggregated_clo_report(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'activity_sheet_report':
        # صفحة تقرير ورقة النشاط
        import importlib
        from pages import activity_sheet_report
        importlib.reload(activity_sheet_report)
        activity_sheet_report.show_activity_sheet_report(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'section_progress_report':
        # صفحة تقرير متابعة الشعب
        import importlib
        from pages import section_progress_report
        importlib.reload(section_progress_report)
        section_progress_report.show_section_progress_report(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'reports' or selected_page == 'my_reports' or selected_page == 'section_reports':
        # استيراد ديناميكي لصفحة التقارير
        import importlib
        from pages import reports
        importlib.reload(reports)
        reports.show_reports(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'assessment':
        st.title(f"📝 {t('assessment', lang)}")
        st.info(f"🚧 {t('under_development', lang)}")
    elif selected_page == 'grades':
        # صفحة إدخال الدرجات للمدرس - توجيه لصفحة درجات الطلاب مع فلترة تلقائية
        import importlib
        from pages import student_grades
        importlib.reload(student_grades)
        student_grades.show_student_grades(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'settings':
        from pages.settings import show_settings
        show_settings(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'stage2_clo_marks':
        # المرحلة 2.1: درجات مخرجات التعلم
        import importlib
        from pages import stage2_clo_marks
        importlib.reload(stage2_clo_marks)
        stage2_clo_marks.show_stage2_clo_marks(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'clo_semester_settings':
        # المرحلة 2.1b: إعدادات CLOs حسب الفصل الدراسي
        import importlib
        from pages import clo_semester_settings
        importlib.reload(clo_semester_settings)
        clo_semester_settings.show_clo_semester_settings(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'stage2_topics_clos':
        # المرحلة 2.2: ربط الموضوعات بمخرجات التعلم
        import importlib
        from pages import stage2_topics_to_clos
        importlib.reload(stage2_topics_to_clos)
        stage2_topics_to_clos.show_stage2_topics_to_clos(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'stage2_topics_activities':
        # المرحلة 2.3: ربط الموضوعات بأنشطة التقييم
        import importlib
        from pages import stage2_topics_to_activities
        importlib.reload(stage2_topics_to_activities)
        stage2_topics_to_activities.show_stage2_topics_to_activities(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'stage2_clos_activities':
        # المرحلة 2.4: توزيع المخرجات على الأنشطة
        import importlib
        from pages import stage2_clos_activities
        importlib.reload(stage2_clos_activities)
        stage2_clos_activities.show_stage2_clos_activities(st.session_state.db, st.session_state.user, lang)
    elif selected_page == 'stage2_specs_table':
        # المرحلة 2.5: جدول المواصفات
        import importlib
        from pages import stage2_specifications_table
        importlib.reload(stage2_specifications_table)
        stage2_specifications_table.show_stage2_specifications_table(st.session_state.db, st.session_state.user, lang)
    elif selected_page.startswith('sep'):
        # عنصر فاصل - لا يفعل شيء
        pass

    st.markdown("</div>", unsafe_allow_html=True)

def show_dashboard(user: User, lang: str):
    """عرض لوحة المعلومات"""

    # إعادة بناء كائن المستخدم من قاعدة البيانات لضمان صحة الأدوار
    db = st.session_state.db
    rebuilt_user = db.get_user_by_username(user.username)
    if rebuilt_user:
        user = rebuilt_user

    is_rtl = lang == 'ar'

    st.title(f"🏠 {t('dashboard', lang)}")

    # جمع الإحصائيات حسب صلاحيات المستخدم
    all_programs = db.get_all_programs()
    all_courses = db.get_all_courses()

    # تصفية البرامج والمقررات حسب دور المستخدم
    if user.role == UserRole.ADMIN:
        # المدير يرى كل شيء
        programs = all_programs
        courses = all_courses
        users_count = len(db.get_all_users())
    elif user.role == UserRole.PROGRAM_COORDINATOR:
        # منسق البرنامج يرى برامجه فقط والمقررات المرتبطة بها
        user_data = db.load_users()
        assigned_programs = []
        for u in user_data:
            if u.get('user_id') == user.user_id:
                assigned_programs = u.get('assigned_programs', [])
                break

        programs = [p for p in all_programs if p.get('program_id') in assigned_programs]
        courses = [c for c in all_courses if c.get('program_id') in assigned_programs]
        users_count = 0  # لا يحتاج لرؤية عدد المستخدمين
    elif user.role == UserRole.COURSE_COORDINATOR:
        # منسق المقرر يرى مقرراته فقط
        user_data = db.load_users()
        assigned_courses = []
        for u in user_data:
            if u.get('user_id') == user.user_id:
                assigned_courses = u.get('assigned_courses', [])
                break

        programs = []  # لا يرى البرامج
        # تصفية المقررات: إما مُسندة له في assigned_courses أو coordinator_id يساوي user_id
        courses = [c for c in all_courses
                  if c.get('course_id') in assigned_courses or c.get('coordinator_id') == user.user_id]
        users_count = 0
    else:
        # مدرس الشعبة - عرض الشعب المسندة إليه
        user_data = db.load_users()
        assigned_sections = {}
        for u in user_data:
            if u.get('user_id') == user.user_id:
                assigned_sections = u.get('assigned_sections', {})
                break

        # جمع المقررات التي لديه شعب فيها
        course_ids = list(assigned_sections.keys())
        courses = [c for c in all_courses if c.get('course_id') in course_ids]

        # جمع البرامج المرتبطة بهذه المقررات
        program_ids = set(c.get('program_id') for c in courses if c.get('program_id'))
        programs = [p for p in all_programs if p.get('program_id') in program_ids]
        users_count = 0

    programs_count = len(programs)
    courses_count = len(courses)

    # حساب البرامج النشطة
    active_programs = len([p for p in programs if p.get('is_active', True)])

    # حساب المقررات النشطة
    active_courses = len([c for c in courses if c.get('is_active', True)])

    # حساب عدد الشعب والطلاب للمدرسين
    sections_count = 0
    students_count = 0
    grades_completion = 0
    assigned_section_ids = set()
    if user.role == UserRole.SECTION_INSTRUCTOR:
        # تحميل بيانات الشعب
        import json
        from pathlib import Path
        sections_file = Path(__file__).parent / 'data' / 'sections.json'
        section_students_file = Path(__file__).parent / 'data' / 'section_students.json'
        student_grades_file = Path(__file__).parent / 'data' / 'student_grades.json'
        try:
            with open(sections_file, 'r', encoding='utf-8') as f:
                sections_data = json.load(f).get('sections', [])
            # احصاء الشعب المسندة للمدرس
            user_data_list = db.load_users()
            assigned_sections = {}
            for u in user_data_list:
                if u.get('user_id') == user.user_id:
                    assigned_sections = u.get('assigned_sections', {})
                    break
            # حساب عدد الشعب
            for course_id, section_numbers in assigned_sections.items():
                sections_count += len(section_numbers)

            # تحميل بيانات طلاب الشعب
            with open(section_students_file, 'r', encoding='utf-8') as f:
                students_data = json.load(f).get('section_students', [])
            # حساب عدد الطلاب في الشعب المسندة
            # أولاً: جمع section_ids للشعب المسندة
            for course_id, section_numbers in assigned_sections.items():
                for section_number in section_numbers:
                    for section in sections_data:
                        if section.get('course_id') == course_id and section.get('section_number') == section_number:
                            assigned_section_ids.add(section.get('section_id'))
            # ثانياً: حساب عدد الطلاب بناءً على section_id
            for student in students_data:
                if student.get('section_id') in assigned_section_ids:
                    students_count += 1

            # حساب نسبة إدخال الدرجات
            with open(student_grades_file, 'r', encoding='utf-8') as f:
                all_grades = json.load(f).get('student_grades', [])
            sections_with_grades = 0
            for section_id in assigned_section_ids:
                section_grades = [g for g in all_grades if g.get('section_id') == section_id]
                if section_grades:
                    sections_with_grades += 1
            grades_completion = int((sections_with_grades / sections_count * 100)) if sections_count > 0 else 0
        except:
            pass

    # بطاقات الإحصائيات
    col1, col2, col3, col4 = st.columns(4)

    if user.role == UserRole.SECTION_INSTRUCTOR:
        # بطاقات خاصة بمدرس الشعبة
        with col1:
            st.markdown(f"""
            <div class="card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <h2 style="color: white;">📖</h2>
                <h3 style="color: white;">{sections_count}</h3>
                <p style="color: white; font-size: 16px;">{"شعبي" if lang == 'ar' else 'My Sections'}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
                <h2 style="color: white;">👨‍🎓</h2>
                <h3 style="color: white;">{students_count}</h3>
                <p style="color: white; font-size: 16px;">{"طلابي" if lang == 'ar' else 'My Students'}</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white;">
                <h2 style="color: white;">📚</h2>
                <h3 style="color: white;">{courses_count}</h3>
                <p style="color: white; font-size: 16px;">{"مقرراتي" if lang == 'ar' else 'My Courses'}</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            # نسبة إدخال الدرجات (تم حسابها مسبقاً)
            st.markdown(f"""
            <div class="card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white;">
                <h2 style="color: white;">✅</h2>
                <h3 style="color: white;">{grades_completion}%</h3>
                <p style="color: white; font-size: 16px;">{"الإنجاز" if lang == 'ar' else 'Progress'}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # البطاقات الأصلية للأدوار الأخرى
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
            if user.role == UserRole.ADMIN:
                st.markdown(f"""
                <div class="card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white;">
                    <h2 style="color: white;">👥</h2>
                    <h3 style="color: white;">{users_count}</h3>
                    <p style="color: white; font-size: 16px;">{t('users', lang)}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="card" style="background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%); color: white;">
                    <h2 style="color: white;">📊</h2>
                    <h3 style="color: white;">{active_programs}</h3>
                    <p style="color: white; font-size: 16px;">{t('active_programs', lang) if lang == 'ar' else 'Active Programs'}</p>
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
        if user.role == UserRole.SECTION_INSTRUCTOR:
            st.markdown(f"""
            <div class="card {'rtl' if is_rtl else 'ltr'}">
                <h3>📊 {"إحصائيات سريعة" if lang == 'ar' else 'Quick Stats'}</h3>
                <p><strong>{"عدد الشعب" if lang == 'ar' else 'My Sections'}:</strong> {sections_count}</p>
                <p><strong>{"عدد الطلاب" if lang == 'ar' else 'My Students'}:</strong> {students_count}</p>
                <p><strong>{"عدد المقررات" if lang == 'ar' else 'My Courses'}:</strong> {courses_count}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="card {'rtl' if is_rtl else 'ltr'}">
                <h3>📊 {t('quick_stats', lang)}</h3>
                <p><strong>{t('active_programs', lang)}:</strong> {active_programs} / {programs_count}</p>
                <p><strong>{t('active_courses', lang)}:</strong> {active_courses} / {courses_count}</p>
                <p><strong>{t('total_users', lang)}:</strong> {users_count}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # عرض آخر البرامج والمقررات (استخدام البيانات المصفاة حسب الصلاحيات)
    if user.role == UserRole.SECTION_INSTRUCTOR:
        # عرض شعب المدرس - عرض شامل ومفصل
        import json
        import pandas as pd
        from pathlib import Path

        sections_file = Path(__file__).parent / 'data' / 'sections.json'
        section_students_file = Path(__file__).parent / 'data' / 'section_students.json'
        student_grades_file = Path(__file__).parent / 'data' / 'student_grades.json'

        try:
            with open(sections_file, 'r', encoding='utf-8') as f:
                all_sections = json.load(f).get('sections', [])
            with open(section_students_file, 'r', encoding='utf-8') as f:
                all_students = json.load(f).get('section_students', [])
            with open(student_grades_file, 'r', encoding='utf-8') as f:
                all_grades = json.load(f).get('student_grades', [])
        except:
            all_sections = []
            all_students = []
            all_grades = []

        user_data_list = db.load_users()
        assigned_sections = {}
        for u in user_data_list:
            if u.get('user_id') == user.user_id:
                assigned_sections = u.get('assigned_sections', {})
                break

        # أزرار الإجراءات السريعة
        st.subheader(f"⚡ {'إجراءات سريعة' if lang == 'ar' else 'Quick Actions'}")
        action_col1, action_col2, action_col3, action_col4 = st.columns(4)

        with action_col1:
            if st.button(f"👥 {'إدارة الطلاب' if lang == 'ar' else 'Manage Students'}", use_container_width=True):
                st.session_state.current_page = 'section_students'
                st.rerun()

        with action_col2:
            if st.button(f"📝 {'إدخال الدرجات' if lang == 'ar' else 'Enter Grades'}", use_container_width=True):
                st.session_state.current_page = 'grades'
                st.rerun()

        with action_col3:
            if st.button(f"📊 {'تقرير CLO' if lang == 'ar' else 'CLO Report'}", use_container_width=True):
                st.session_state.current_page = 'clo_report'
                st.rerun()

        with action_col4:
            if st.button(f"📈 {'لوحة الدرجات' if lang == 'ar' else 'Grades Dashboard'}", use_container_width=True):
                st.session_state.current_page = 'grades_dashboard'
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # جدول تفصيلي للشعب
        st.subheader(f"📋 {'تفاصيل شعبي الدراسية' if lang == 'ar' else 'My Sections Details'}")

        if not assigned_sections:
            st.info("لا توجد شعب مسندة حالياً" if lang == 'ar' else "No sections assigned yet")
        else:
            sections_data_list = []
            sections_with_grades = 0

            for course_id, section_numbers in assigned_sections.items():
                course_info = next((c for c in all_courses if c.get('course_id') == course_id), None)
                course_code = course_info.get('course_code', '') if course_info else ''
                course_name = course_info.get('course_title_ar' if lang == 'ar' else 'course_title_en', '') if course_info else ''

                for section_number in section_numbers:
                    # معلومات الشعبة
                    section_info = next((s for s in all_sections
                                        if s.get('course_id') == course_id and s.get('section_number') == section_number), None)

                    # الحصول على section_id
                    section_id = section_info.get('section_id') if section_info else None

                    # عدد الطلاب باستخدام section_id
                    if section_id:
                        section_students = [s for s in all_students if s.get('section_id') == section_id]
                    else:
                        section_students = []

                    # التحقق من وجود درجات باستخدام section_id
                    if section_id:
                        section_grades = [g for g in all_grades if g.get('section_id') == section_id]
                    else:
                        section_grades = []
                    has_grades = len(section_grades) > 0
                    if has_grades:
                        sections_with_grades += 1

                    grades_status = "✅" if has_grades else "❌"

                    sections_data_list.append({
                        'رمز المقرر': course_code,
                        'اسم المقرر': course_name,
                        'رقم الشعبة': section_number,
                        'الفصل الدراسي': section_info.get('semester', '') if section_info else '',
                        'عدد الطلاب': len(section_students),
                        'الدرجات': grades_status
                    })

            if sections_data_list:
                df_sections = pd.DataFrame(sections_data_list)
                st.dataframe(df_sections, use_container_width=True, hide_index=True)

                # ملخص إضافي
                st.markdown("<br>", unsafe_allow_html=True)
                total_sections = len(sections_data_list)
                completion_rate = int((sections_with_grades / total_sections * 100)) if total_sections > 0 else 0

                summary_col1, summary_col2 = st.columns(2)
                with summary_col1:
                    st.info(f"📊 {'نسبة إدخال الدرجات' if lang == 'ar' else 'Grades Entry Progress'}: **{completion_rate}%** ({sections_with_grades}/{total_sections})")
                with summary_col2:
                    total_students_in_table = sum(row['عدد الطلاب'] for row in sections_data_list)
                    st.info(f"👨‍🎓 {'إجمالي الطلاب' if lang == 'ar' else 'Total Students'}: **{total_students_in_table}**")

    elif user.role in [UserRole.ADMIN, UserRole.PROGRAM_COORDINATOR]:
        st.subheader(f"📌 {t('recent_activity', lang)}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{t('recent_programs', lang)}**")
            # استخدام المتغير programs المصفى بدلاً من db.get_all_programs()
            if programs:
                # عرض آخر 3 برامج من البرامج المصفاة
                recent_programs = programs[-3:] if len(programs) > 3 else programs
                for program in recent_programs:
                    program_name = program.get('program_name_ar' if lang == 'ar' else 'program_name_en', '')
                    status = '🟢' if program.get('is_active', True) else '🔴'
                    st.write(f"{status} {program.get('program_code', '')} - {program_name}")
            else:
                st.info(t('no_programs_yet', lang))

        with col2:
            st.markdown(f"**{t('recent_courses', lang)}**")
            # استخدام المتغير courses المصفى بدلاً من db.get_all_courses()
            if courses:
                # عرض آخر 3 مقررات من المقررات المصفاة
                recent_courses = courses[-3:] if len(courses) > 3 else courses
                for course in recent_courses:
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

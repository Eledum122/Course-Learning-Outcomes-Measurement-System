"""
صفحة الإعدادات - Settings Page
إدارة إعدادات النظام والملف الشخصي والمعلومات
"""

import streamlit as st
from datetime import datetime
import hashlib
import shutil
import os
from pathlib import Path
from models.database import Database, User, UserRole
from translations import t


def hash_password(password: str) -> str:
    """تشفير كلمة المرور باستخدام SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def show_settings(db: Database, user: User, lang: str):
    """عرض صفحة الإعدادات"""

    # إعادة بناء كائن المستخدم من قاعدة البيانات لضمان صحة الأدوار
    user = db.get_user_by_username(user.username)
    if not user:
        st.error("⛔ خطأ في تحميل بيانات المستخدم")
        return

    is_rtl = lang == 'ar'

    # العنوان الرئيسي
    st.title(f"⚙️ {t('settings', lang)}")

    # Tabs للأقسام المختلفة
    if user.role == UserRole.ADMIN:
        tabs = st.tabs([
            f"👤 {t('user_profile', lang)}",
            f"ℹ️ {t('about_system', lang)}",
            f"📊 {t('system_statistics', lang)}",
            f"💾 {t('database_management', lang)}"
        ])
    else:
        tabs = st.tabs([
            f"👤 {t('user_profile', lang)}",
            f"ℹ️ {t('about_system', lang)}",
            f"📊 {t('system_statistics', lang)}"
        ])

    # Tab 1: User Profile
    with tabs[0]:
        show_user_profile(db, user, lang, is_rtl)

    # Tab 2: About System
    with tabs[1]:
        show_about_system(lang, is_rtl)

    # Tab 3: System Statistics
    with tabs[2]:
        show_system_statistics(db, lang, is_rtl)

    # Tab 4: Database Management (Admin only)
    if user.role == UserRole.ADMIN and len(tabs) > 3:
        with tabs[3]:
            show_database_management(db, lang, is_rtl)


def show_user_profile(db: Database, user: User, lang: str, is_rtl: bool):
    """عرض معلومات المستخدم وإمكانية التعديل"""

    st.subheader(f"👤 {t('user_profile', lang)}")

    # معلومات المستخدم الأساسية
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;'>
            <h3 style='margin: 0; color: white;'>{user.full_name}</h3>
            <p style='margin: 5px 0; opacity: 0.9;'>@{user.username}</p>
            <p style='margin: 5px 0; opacity: 0.9;'>🎭 {t(user.role.value, lang)}</p>
        </div>
        """, unsafe_allow_html=True)

        # معلومات إضافية
        st.markdown(f"**{t('employee_id', lang)}:** {user.employee_id or '-'}")
        st.markdown(f"**{t('email_address', lang)}:** {user.email or '-'}")

        # Handle created_date - check if attribute exists
        created_date = '-'
        if hasattr(user, 'created_date') and user.created_date:
            created_date = user.created_date.split('T')[0]
        st.markdown(f"**{t('account_created', lang)}:** {created_date}")

        # Handle last_login - check if attribute exists
        last_login = t('never', lang)
        if hasattr(user, 'last_login') and user.last_login:
            last_login = user.last_login.split('T')[0]
        st.markdown(f"**{t('last_login', lang)}:** {last_login}")

    with col2:
        # صلاحيات المستخدم
        st.markdown(f"### {t('permissions', lang)}")

        # Show user roles
        st.markdown(f"**{t('user_role', lang)}:**")
        st.markdown(f"🎭 **{t(user.role.value, lang)}**")

        st.markdown("")  # spacing

        # Additional info
        all_programs = len(db.get_all_programs())
        all_courses = len(db.get_all_courses())
        all_users = len(db.get_all_users())

        if user.role == UserRole.ADMIN:
            st.markdown(f"""
            **{t('access_level', lang) if lang == 'ar' else 'Access Level'}:**
            - ✅ {t('full_system_access', lang) if lang == 'ar' else 'Full System Access'}
            - ✅ {t('manage_all_users', lang) if lang == 'ar' else 'Manage All Users'}
            - ✅ {t('manage_all_programs', lang) if lang == 'ar' else 'Manage All Programs'}
            - ✅ {t('manage_all_courses', lang) if lang == 'ar' else 'Manage All Courses'}
            - ✅ {t('view_all_reports', lang) if lang == 'ar' else 'View All Reports'}
            """)

    st.divider()

    # تحديث البريد الإلكتروني
    st.subheader(f"📧 {t('update_email', lang)}")

    with st.form("update_email_form", clear_on_submit=True):
        new_email = st.text_input(
            t('new_email', lang),
            value=user.email or "",
            placeholder="example@university.edu.sa"
        )

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submit_email = st.form_submit_button(
                t('save', lang),
                use_container_width=True,
                type="primary"
            )
        with col2:
            cancel_email = st.form_submit_button(
                t('cancel', lang),
                use_container_width=True
            )

        if submit_email and new_email:
            if db.update_user(
                user_id=user.user_id,
                email=new_email
            ):
                st.success(t('email_updated_successfully', lang))
                # تحديث معلومات المستخدم في الجلسة
                st.session_state.user = db.get_user_by_id(user.user_id)
                st.rerun()
            else:
                st.error(t('email_update_failed', lang))

    st.divider()

    # تغيير كلمة المرور
    st.subheader(f"🔐 {t('change_password', lang)}")

    with st.form("change_password_form", clear_on_submit=True):
        current_password = st.text_input(
            t('current_password', lang),
            type="password",
            placeholder="••••••••"
        )

        new_password = st.text_input(
            t('new_password', lang),
            type="password",
            placeholder="••••••••"
        )

        confirm_password = st.text_input(
            t('confirm_new_password', lang),
            type="password",
            placeholder="••••••••"
        )

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submit_password = st.form_submit_button(
                t('change_password', lang),
                use_container_width=True,
                type="primary"
            )
        with col2:
            cancel_password = st.form_submit_button(
                t('cancel', lang),
                use_container_width=True
            )

        if submit_password:
            # التحقق من كلمة المرور الحالية
            if hash_password(current_password) != user.password_hash:
                st.error(t('current_password_incorrect', lang))
            elif len(new_password) < 6:
                st.error(t('password_too_short', lang))
            elif new_password != confirm_password:
                st.error(t('passwords_not_match', lang))
            else:
                # تحديث كلمة المرور
                new_hash = hash_password(new_password)
                if db.update_user(user_id=user.user_id, password_hash=new_hash):
                    st.success(t('password_changed_successfully', lang))
                    st.info("🔄 " + t('please_login_again', lang) if lang == 'ar' else "🔄 Please login again with your new password")
                else:
                    st.error(t('password_change_failed', lang))


def show_about_system(lang: str, is_rtl: bool):
    """عرض معلومات عن النظام"""

    st.subheader(f"ℹ️ {t('about_system', lang)}")

    # معلومات النظام
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 30px; border-radius: 15px; color: white; margin-bottom: 20px; text-align: center;'>
        <h1 style='margin: 0; color: white;'>🎓 {t('app_title', lang)}</h1>
        <p style='margin: 10px 0; font-size: 18px; opacity: 0.95;'>{t('system_description', lang)}</p>
        <p style='margin: 10px 0; opacity: 0.9;'>{t('version', lang)}: 1.0.0</p>
    </div>
    """, unsafe_allow_html=True)

    # تفاصيل النظام
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        ### 📋 {t('system_information', lang)}

        - **{t('system_name', lang)}:** CLOs Measurement System
        - **{t('system_version', lang)}:** 1.0.0
        - **{t('developer', lang)}:** Academic Assessment Team
        - **{t('development_year', lang)}:** 2025-2026
        - **{t('database_type', lang)}:** JSON-based Storage
        """)

    with col2:
        st.markdown(f"""
        ### 🛠️ {t('technology_stack', lang)}

        - **Frontend:** Streamlit
        - **Backend:** Python 3.11+
        - **Database:** JSON Files
        - **Security:** SHA256 Password Hashing
        - **UI Framework:** Custom CSS + Streamlit
        """)

    st.divider()

    # مميزات النظام
    st.markdown(f"### ✨ {t('system_features', lang)}")

    features = [
        ('👥', 'feature_users_management'),
        ('🏛️', 'feature_programs_management'),
        ('📚', 'feature_courses_management'),
        ('🎯', 'feature_clos_management'),
        ('📊', 'feature_reports'),
        ('🌐', 'feature_bilingual')
    ]

    cols = st.columns(3)
    for idx, (icon, feature_key) in enumerate(features):
        with cols[idx % 3]:
            st.markdown(f"""
            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px;
                        text-align: center; margin-bottom: 10px; border: 2px solid #e9ecef;'>
                <div style='font-size: 32px; margin-bottom: 10px;'>{icon}</div>
                <div style='font-size: 14px; color: #495057;'>{t(feature_key, lang)}</div>
            </div>
            """, unsafe_allow_html=True)


def show_system_statistics(db: Database, lang: str, is_rtl: bool):
    """عرض إحصائيات النظام"""

    st.subheader(f"📊 {t('system_statistics', lang)}")

    # جمع الإحصائيات
    all_users = db.get_all_users()
    all_programs = db.get_all_programs()
    all_courses = db.get_all_courses()

    # عرض الإحصائيات في بطاقات
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <h1 style='margin: 0; color: white;'>{len(all_users)}</h1>
            <p style='margin: 5px 0;'>{t('total_users', lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <h1 style='margin: 0; color: white;'>{len(all_programs)}</h1>
            <p style='margin: 5px 0;'>{t('total_programs', lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <h1 style='margin: 0; color: white;'>{len(all_courses)}</h1>
            <p style='margin: 5px 0;'>{t('total_courses', lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        active_programs = len([p for p in all_programs if p.get('is_active', True)])
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <h1 style='margin: 0; color: white;'>{active_programs}</h1>
            <p style='margin: 5px 0;'>{t('active_programs', lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # إحصائيات المستخدمين حسب الدور
    st.markdown(f"### 👥 {t('users_by_role', lang) if lang == 'ar' else 'Users by Role'}")

    role_counts = {}
    for user_obj in all_users:
        # user_obj is a User object, so access roles attribute directly
        for role in user_obj.roles:
            role_counts[role] = role_counts.get(role, 0) + 1

    cols = st.columns(4)
    role_colors = {
        'admin': '#667eea',
        'program_coordinator': '#f093fb',
        'course_coordinator': '#4facfe',
        'section_instructor': '#43e97b'
    }

    for idx, (role, count) in enumerate(role_counts.items()):
        with cols[idx % 4]:
            color = role_colors.get(role, '#6c757d')
            st.markdown(f"""
            <div style='background-color: {color}; padding: 15px; border-radius: 8px;
                        color: white; text-align: center; margin-bottom: 10px;'>
                <h2 style='margin: 0; color: white;'>{count}</h2>
                <p style='margin: 5px 0; font-size: 14px;'>{t(role, lang)}</p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # إحصائيات المقررات حسب البرنامج
    if all_programs:
        st.markdown(f"### 📚 {t('courses_by_program', lang) if lang == 'ar' else 'Courses by Program'}")

        program_courses = {}
        for course in all_courses:
            prog_id = course.get('program_id', '')
            program_courses[prog_id] = program_courses.get(prog_id, 0) + 1

        # عرض في جدول
        import pandas as pd

        program_stats = []
        for program in all_programs:
            prog_id = program.get('program_id', '')
            course_count = program_courses.get(prog_id, 0)
            program_stats.append({
                t('program_code', lang): program.get('program_code', ''),
                t('program_name', lang): program.get('program_name_ar' if lang == 'ar' else 'program_name_en', ''),
                t('total_courses', lang): course_count,
                t('status', lang): '🟢 ' + t('active', lang) if program.get('is_active', True) else '🔴 ' + t('inactive', lang)
            })

        if program_stats:
            df = pd.DataFrame(program_stats)
            st.dataframe(df, use_container_width=True, hide_index=True)


def show_database_management(db: Database, lang: str, is_rtl: bool):
    """إدارة قاعدة البيانات (للمدير فقط)"""

    st.subheader(f"💾 {t('database_management', lang)}")

    st.warning("⚠️ " + (
        "هذه الميزات متقدمة وتؤثر على البيانات. يرجى استخدامها بحذر."
        if lang == 'ar' else
        "These are advanced features that affect your data. Please use with caution."
    ))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### 📦 {t('backup_database', lang)}")
        st.markdown(
            "إنشاء نسخة احتياطية من جميع بيانات النظام"
            if lang == 'ar' else
            "Create a backup of all system data"
        )

        if st.button(
            f"💾 {t('backup_database', lang)}",
            use_container_width=True,
            type="primary"
        ):
            try:
                # إنشاء مجلد النسخ الاحتياطية إذا لم يكن موجوداً
                backup_dir = Path("data/backups")
                backup_dir.mkdir(parents=True, exist_ok=True)

                # إنشاء اسم الملف بالتاريخ والوقت
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_dir / f"backup_{timestamp}"
                backup_path.mkdir(exist_ok=True)

                # نسخ ملفات البيانات
                data_files = ['users.json', 'programs.json', 'courses.json']
                for file in data_files:
                    src = Path(f"data/{file}")
                    if src.exists():
                        dst = backup_path / file
                        shutil.copy2(src, dst)

                st.success(f"✅ {t('backup_created_successfully', lang)}")
                st.info(f"📁 {backup_path}")

            except Exception as e:
                st.error(f"{t('backup_failed', lang)}: {str(e)}")

    with col2:
        st.markdown(f"### 📊 {t('database_info', lang) if lang == 'ar' else 'Database Information'}")

        # معلومات عن الملفات
        data_dir = Path("data")
        if data_dir.exists():
            data_files = list(data_dir.glob("*.json"))

            for file in data_files:
                file_size = file.stat().st_size / 1024  # KB
                modified = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")

                st.markdown(f"""
                <div style='background-color: #f8f9fa; padding: 10px; border-radius: 8px;
                            margin-bottom: 10px; border-left: 4px solid #007bff;'>
                    <strong>{file.name}</strong><br>
                    <small>📏 {file_size:.2f} KB | 🕒 {modified}</small>
                </div>
                """, unsafe_allow_html=True)

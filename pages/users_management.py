"""
صفحة إدارة المستخدمين
Users Management Page
"""

import streamlit as st
import pandas as pd
import json
import hashlib
import secrets
from datetime import datetime
from models.database import Database, UserRole
from translations import t


def load_faculty_members():
    """تحميل أعضاء هيئة التدريس"""
    try:
        with open('data/faculty.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('faculty_members', [])
    except:
        return []


def load_programs():
    """تحميل البرامج"""
    try:
        with open('data/programs.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('programs', [])
    except:
        return []


def load_courses():
    """تحميل المقررات"""
    try:
        with open('data/courses.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('courses', [])
    except:
        return []


def load_sections():
    """تحميل الشعب"""
    try:
        with open('data/sections.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('sections', [])
    except:
        return []


def load_course_coordinators():
    """تحميل منسقي المقررات"""
    try:
        with open('data/course_coordinators.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('course_coordinators', [])
    except:
        return []


def get_faculty_assigned_programs(employee_id: str, programs: list) -> list:
    """
    Get programs where the faculty member is assigned as coordinator
    البرامج التي تم تعيين عضو هيئة التدريس فيها كمنسق
    """
    assigned = []
    for p in programs:
        # Check if coordinator_id matches (could be user_id or employee_id)
        coord_id = p.get('coordinator_id', '')
        if coord_id == employee_id:
            assigned.append(p)
    return assigned


def get_faculty_assigned_courses(employee_id: str, courses: list, course_coordinators: list) -> list:
    """
    Get courses where the faculty member is assigned as coordinator
    المقررات التي تم تعيين عضو هيئة التدريس فيها كمنسق
    """
    assigned_course_ids = set()

    # Check course_coordinators.json for assignments
    for coord in course_coordinators:
        if coord.get('coordinator_id') == employee_id:
            assigned_course_ids.add(coord.get('course_id'))

    # Return matching courses
    return [c for c in courses if c.get('course_id') in assigned_course_ids]


def get_faculty_assigned_sections(employee_id: str, sections: list) -> list:
    """
    Get sections where the faculty member is assigned as instructor
    الشعب التي تم تعيين عضو هيئة التدريس فيها كمدرس
    """
    return [s for s in sections if s.get('instructor_id') == employee_id]


def generate_username(faculty_member):
    """إنشاء اسم مستخدم تلقائي من عضو هيئة التدريس"""
    name = faculty_member.get('name', '')
    employee_id = faculty_member.get('employee_id', '')

    # أخذ أول حرف من الاسم + رقم الموظف
    first_letter = name[0].upper() if name else 'U'
    return f"{first_letter}{employee_id}"


def generate_password():
    """إنشاء كلمة مرور عشوائية"""
    return secrets.token_urlsafe(8)


def show_users_management(db: Database, user, lang: str):
    """عرض صفحة إدارة المستخدمين"""

    # إعادة بناء كائن المستخدم من قاعدة البيانات لضمان صحة الأدوار
    rebuilt_user = db.get_user_by_username(user.username)
    if not rebuilt_user:
        st.error("⛔ خطأ في تحميل بيانات المستخدم")
        return

    user = rebuilt_user
    is_rtl = lang == 'ar'

    st.title(f"👥 {t('users_management', lang)}")

    # التحقق من الصلاحيات
    if user.role != UserRole.ADMIN:
        st.error(f"⛔ {t('no_permission', lang)}")
        return

    # علامات التبويب
    tab1, tab2, tab3 = st.tabs([
        f"📋 {t('users_list', lang)}",
        f"➕ {t('add_user', lang)}",
        f"✏️ تعديل المستخدمين / Edit Users"
    ])

    # علامة التبويب الأولى: قائمة المستخدمين
    with tab1:
        show_users_list(db, lang, is_rtl)

    # علامة التبويب الثانية: إضافة مستخدم
    with tab2:
        show_add_user_form(db, lang, is_rtl)

    # علامة التبويب الثالثة: تعديل المستخدمين
    with tab3:
        show_edit_users(db, lang, is_rtl)


def show_users_list(db: Database, lang: str, is_rtl: bool):
    """عرض قائمة المستخدمين"""

    st.subheader(f"📋 {t('users_list', lang)}")

    # تحميل المستخدمين
    users = db.get_all_users()

    if not users:
        st.info(f"ℹ️ {t('no_users_found', lang)}")
        return

    # تحميل البيانات المرجعية
    programs = load_programs()
    courses = load_courses()
    sections = load_sections()

    programs_dict = {p['program_id']: p for p in programs}
    courses_dict = {c['course_id']: c for c in courses}

    # تحويل إلى DataFrame
    users_data = []
    for u in users:
        # الحصول على أسماء البرامج المعينة
        assigned_programs_names = []
        for prog_id in u.assigned_programs:
            prog = programs_dict.get(prog_id)
            if prog:
                assigned_programs_names.append(prog.get('program_code', prog_id))

        # الحصول على أسماء المقررات المعينة
        assigned_courses_names = []
        for course_id in u.assigned_courses:
            course = courses_dict.get(course_id)
            if course:
                assigned_courses_names.append(course.get('course_code', course_id))

        # الحصول على أسماء الشعب المعينة
        assigned_sections_display = []
        if hasattr(u, 'assigned_sections') and u.assigned_sections:
            for course_id, section_nums in u.assigned_sections.items():
                course = courses_dict.get(course_id)
                course_code = course.get('course_code', course_id) if course else course_id
                for sec_num in section_nums:
                    assigned_sections_display.append(f"{course_code}-{sec_num}")

        users_data.append({
            'user_id': u.user_id,
            'username': u.username,
            'full_name': u.full_name,
            'email': u.email,
            'roles': ', '.join(u.roles),
            'employee_id': u.employee_id,
            'programs': ', '.join(assigned_programs_names) if assigned_programs_names else '-',
            'courses': ', '.join(assigned_courses_names) if assigned_courses_names else '-',
            'sections': ', '.join(assigned_sections_display) if assigned_sections_display else '-',
            'is_active': '✅' if hasattr(u, 'is_active') and u.is_active else '❌'
        })

    df = pd.DataFrame(users_data)

    # عرض الجدول
    st.dataframe(
        df,
        column_config={
            'user_id': st.column_config.TextColumn(t('user_id', lang), width='small'),
            'username': st.column_config.TextColumn(t('username', lang), width='medium'),
            'full_name': st.column_config.TextColumn(t('full_name', lang), width='medium'),
            'email': st.column_config.TextColumn(t('email', lang), width='medium'),
            'roles': st.column_config.TextColumn(t('roles', lang), width='medium'),
            'employee_id': st.column_config.TextColumn(t('employee_id', lang), width='small'),
            'programs': st.column_config.TextColumn('البرامج / Programs', width='medium'),
            'courses': st.column_config.TextColumn('المقررات / Courses', width='medium'),
            'sections': st.column_config.TextColumn('الشعب / Sections', width='medium'),
            'is_active': st.column_config.TextColumn(t('status', lang), width='small')
        },
        hide_index=True,
        use_container_width=True
    )

    st.info(f"📊 {t('total_users', lang)}: {len(users)}")


def show_add_user_form(db: Database, lang: str, is_rtl: bool):
    """عرض نموذج إضافة مستخدم"""

    st.subheader(f"➕ {t('add_new_user', lang)}")

    # تحميل البيانات
    faculty_members = load_faculty_members()
    programs = load_programs()
    courses = load_courses()
    sections = load_sections()
    course_coordinators = load_course_coordinators()

    if not faculty_members:
        st.warning("⚠️ لا يوجد أعضاء هيئة تدريس. يرجى إضافة أعضاء هيئة التدريس أولاً / No faculty members found. Please add faculty members first.")
        return

    st.info("💡 يجب أن يكون المستخدم من أعضاء هيئة التدريس المسجلين / User must be a registered faculty member")

    # اختيار عضو هيئة التدريس
    faculty_options = {f"{fm['name']} ({fm['employee_id']})": fm for fm in faculty_members}
    selected_faculty_key = st.selectbox(
        "اختر عضو هيئة التدريس / Select Faculty Member *",
        options=list(faculty_options.keys()),
        key="add_faculty_select"
    )

    selected_faculty = faculty_options.get(selected_faculty_key)

    # Get pre-assigned roles for the selected faculty member
    faculty_employee_id = selected_faculty.get('employee_id', '') if selected_faculty else ''
    faculty_assigned_programs = get_faculty_assigned_programs(faculty_employee_id, programs)
    faculty_assigned_courses = get_faculty_assigned_courses(faculty_employee_id, courses, course_coordinators)
    faculty_assigned_sections = get_faculty_assigned_sections(faculty_employee_id, sections)

    if selected_faculty:
        # عرض معلومات العضو المختار
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("الاسم / Name", value=selected_faculty.get('name', ''), disabled=True)
            st.text_input("رقم الموظف / Employee ID", value=selected_faculty.get('employee_id', ''), disabled=True)
        with col2:
            st.text_input("البريد الإلكتروني / Email", value=selected_faculty.get('email', ''), disabled=True)
            st.text_input("القسم / Department", value=selected_faculty.get('department', ''), disabled=True)

        # إنشاء اسم المستخدم تلقائياً
        auto_username = generate_username(selected_faculty)
        st.info(f"📝 اسم المستخدم المقترح / Suggested username: **{auto_username}**")

        # اختيار الأدوار
        st.markdown("### 🎭 اختيار الأدوار / Select Roles *")
        st.caption("يمكن للمستخدم الجمع بين عدة أدوار / User can have multiple roles")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            is_admin = st.checkbox(f"🔐 {t('admin', lang)}", key="add_role_admin")
        with col2:
            is_program_coord = st.checkbox(f"🏛️ {t('program_coordinator', lang)}", key="add_role_program_coord")
        with col3:
            is_course_coord = st.checkbox(f"📚 {t('course_coordinator', lang)}", key="add_role_course_coord")
        with col4:
            is_section_instructor = st.checkbox(f"👨‍🏫 {t('section_instructor', lang)}", key="add_role_section_instructor")

        # اختيار البرامج إذا كان منسق برنامج
        selected_programs = []
        if is_program_coord:
            st.markdown("#### 🏛️ اختيار البرامج / Select Programs")
            # Show only programs where this faculty member is already assigned as coordinator
            if faculty_assigned_programs:
                program_options = {f"{p['program_code']} - {p['program_name_en']}": p['program_id'] for p in faculty_assigned_programs}
                selected_program_keys = st.multiselect(
                    "اختر البرامج المعينة / Select Assigned Programs *",
                    options=list(program_options.keys()),
                    default=list(program_options.keys()),  # Pre-select all assigned programs
                    key="add_programs_select"
                )
                selected_programs = [program_options[k] for k in selected_program_keys]
                st.info(f"💡 يظهر فقط البرامج التي تم تعيين {selected_faculty.get('name', '')} كمنسق لها")
            else:
                st.warning(f"⚠️ لم يتم تعيين {selected_faculty.get('name', '')} كمنسق لأي برنامج بعد / Not assigned as coordinator for any program yet")
                st.info("💡 يجب أولاً تعيين عضو هيئة التدريس كمنسق برنامج من صفحة إدارة البرامج")

        # اختيار المقررات إذا كان منسق مقرر
        selected_courses = []
        if is_course_coord:
            st.markdown("#### 📚 اختيار المقررات / Select Courses")
            # Show only courses where this faculty member is already assigned as coordinator
            if faculty_assigned_courses:
                course_options = {f"{c['course_code']} - {c['course_title_en']}": c['course_id'] for c in faculty_assigned_courses}
                selected_course_keys = st.multiselect(
                    "اختر المقررات المعينة / Select Assigned Courses *",
                    options=list(course_options.keys()),
                    default=list(course_options.keys()),  # Pre-select all assigned courses
                    key="add_courses_select"
                )
                selected_courses = [course_options[k] for k in selected_course_keys]
                st.info(f"💡 يظهر فقط المقررات التي تم تعيين {selected_faculty.get('name', '')} كمنسق لها")
            else:
                st.warning(f"⚠️ لم يتم تعيين {selected_faculty.get('name', '')} كمنسق لأي مقرر بعد / Not assigned as coordinator for any course yet")
                st.info("💡 يجب أولاً تعيين عضو هيئة التدريس كمنسق مقرر من صفحة إدارة الشعب")

        # اختيار الشعب إذا كان مدرس شعبة
        selected_sections = {}
        if is_section_instructor:
            st.markdown("#### 👨‍🏫 اختيار الشعب / Select Sections")

            # Show only sections where this faculty member is already assigned as instructor
            if faculty_assigned_sections:
                # عرض الشعب المعينة فقط
                section_options = {}
                for sec in faculty_assigned_sections:
                    course_id = sec.get('course_id')
                    course = next((c for c in courses if c['course_id'] == course_id), None)
                    if course:
                        course_code = course.get('course_code', course_id)
                        sec_num = sec.get('section_number', '')
                        semester = sec.get('semester_code', '')
                        year = sec.get('academic_year', '')
                        key = f"{course_code} - Section {sec_num} ({semester}/{year})"
                        section_options[key] = {'course_id': course_id, 'section_number': sec_num}

                if section_options:
                    selected_section_keys = st.multiselect(
                        "اختر الشعب المعينة / Select Assigned Sections *",
                        options=list(section_options.keys()),
                        default=list(section_options.keys()),  # Pre-select all assigned sections
                        key="add_sections_select"
                    )

                    # تجميع الشعب المختارة
                    for key in selected_section_keys:
                        sec_info = section_options[key]
                        course_id = sec_info['course_id']
                        sec_num = sec_info['section_number']
                        if course_id not in selected_sections:
                            selected_sections[course_id] = []
                        selected_sections[course_id].append(sec_num)

                    st.info(f"💡 يظهر فقط الشعب التي تم تعيين {selected_faculty.get('name', '')} كمدرس لها")
            else:
                st.warning(f"⚠️ لم يتم تعيين {selected_faculty.get('name', '')} كمدرس لأي شعبة بعد / Not assigned as instructor for any section yet")
                st.info("💡 يجب أولاً تعيين عضو هيئة التدريس كمدرس شعبة من صفحة إدارة الشعب")

        # كلمة المرور
        st.markdown("### 🔑 كلمة المرور / Password")

        auto_password = generate_password()
        use_auto_password = st.checkbox("إنشاء كلمة مرور تلقائية / Generate automatic password", value=True, key="add_auto_password")

        if use_auto_password:
            password = auto_password
            st.info(f"🔑 كلمة المرور المولدة / Generated password: **{auto_password}**")
            st.warning("⚠️ يرجى حفظ كلمة المرور قبل إضافة المستخدم / Please save the password before adding the user")
        else:
            col1, col2 = st.columns(2)
            with col1:
                password = st.text_input("كلمة المرور / Password *", type="password", key="add_password")
            with col2:
                confirm_password = st.text_input("تأكيد كلمة المرور / Confirm Password *", type="password", key="add_confirm_password")

        # زر الإضافة
        if st.button(f"➕ {t('add_user', lang)}", type="primary", use_container_width=True, key="add_user_btn"):
            # التحقق من الأدوار
            if not (is_admin or is_program_coord or is_course_coord or is_section_instructor):
                st.error("⚠️ يرجى اختيار دور واحد على الأقل / Please select at least one role")
                return

            # التحقق من البرامج لمنسق البرنامج
            if is_program_coord and not selected_programs:
                st.error("⚠️ يرجى اختيار برنامج واحد على الأقل / Please select at least one program")
                return

            # التحقق من المقررات لمنسق المقرر
            if is_course_coord and not selected_courses:
                st.error("⚠️ يرجى اختيار مقرر واحد على الأقل / Please select at least one course")
                return

            # التحقق من الشعب لمدرس الشعبة
            if is_section_instructor and not selected_sections:
                st.error("⚠️ يرجى اختيار شعبة واحدة على الأقل / Please select at least one section")
                return

            # التحقق من كلمة المرور
            if not use_auto_password:
                if not password:
                    st.error("⚠️ يرجى إدخال كلمة المرور / Please enter a password")
                    return
                if password != confirm_password:
                    st.error(f"⚠️ {t('passwords_do_not_match', lang)}")
                    return

            # إنشاء قائمة الأدوار
            roles = []
            if is_admin:
                roles.append("admin")
            if is_program_coord:
                roles.append("program_coordinator")
            if is_course_coord:
                roles.append("course_coordinator")
            if is_section_instructor:
                roles.append("section_instructor")

            # تشفير كلمة المرور
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            # إنشاء ID للمستخدم
            user_id = f"user_{secrets.token_hex(3)}"

            # بيانات المستخدم الجديد
            new_user_data = {
                "user_id": user_id,
                "username": auto_username,
                "password_hash": password_hash,
                "full_name": selected_faculty.get('name', ''),
                "email": selected_faculty.get('email', ''),
                "roles": roles,
                "employee_id": selected_faculty.get('employee_id', ''),
                "faculty_id": selected_faculty.get('employee_id', ''),
                "assigned_programs": selected_programs,
                "assigned_courses": selected_courses,
                "assigned_sections": selected_sections,
                "created_date": datetime.now().isoformat(),
                "last_login": None,
                "is_active": True,
                "metadata": {}
            }

            # حفظ المستخدم
            users = db.load_users()

            # التحقق من عدم تكرار اسم المستخدم
            if any(u.get('username') == auto_username for u in users):
                st.error(f"⚠️ {t('username_already_exists', lang)}")
                return

            users.append(new_user_data)

            with open(db.users_file, 'w', encoding='utf-8') as f:
                json.dump({"users": users, "last_updated": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)

            st.success(f"✅ {t('user_added_successfully', lang)}")
            st.info(f"📝 اسم المستخدم / Username: **{auto_username}**")
            if use_auto_password:
                st.info(f"🔑 كلمة المرور / Password: **{auto_password}**")
            st.rerun()


def show_edit_users(db: Database, lang: str, is_rtl: bool):
    """عرض صفحة تعديل المستخدمين"""

    st.subheader("✏️ تعديل المستخدمين / Edit Users")

    users = db.load_users()

    if not users:
        st.info("ℹ️ لا يوجد مستخدمين / No users found")
        return

    # تحميل البيانات المرجعية
    programs = load_programs()
    courses = load_courses()
    sections = load_sections()
    faculty_members = load_faculty_members()

    # اختيار المستخدم للتعديل
    user_options = {f"{u.get('full_name', '')} ({u.get('username', '')})": u for u in users}
    selected_user_key = st.selectbox(
        "اختر المستخدم للتعديل / Select User to Edit",
        options=list(user_options.keys()),
        key="edit_user_select"
    )

    selected_user = user_options.get(selected_user_key)

    if selected_user:
        # استخدام user_id كجزء من key لضمان تحديث البيانات عند تغيير المستخدم
        user_key = selected_user.get('user_id', 'unknown')

        st.markdown("---")

        # عرض معلومات المستخدم
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📝 معلومات المستخدم / User Information")
            st.text_input("اسم المستخدم / Username", value=selected_user.get('username', ''), disabled=True, key=f"edit_username_{user_key}")
            new_full_name = st.text_input("الاسم الكامل / Full Name", value=selected_user.get('full_name', ''), key=f"edit_fullname_{user_key}")
            new_email = st.text_input("البريد الإلكتروني / Email", value=selected_user.get('email', ''), key=f"edit_email_{user_key}")

        with col2:
            st.markdown("### 🔑 تغيير كلمة المرور / Change Password")
            change_password = st.checkbox("تغيير كلمة المرور / Change Password", key=f"edit_change_password_{user_key}")

            if change_password:
                new_password = st.text_input("كلمة المرور الجديدة / New Password", type="password", key=f"edit_new_password_{user_key}")
                confirm_new_password = st.text_input("تأكيد كلمة المرور / Confirm Password", type="password", key=f"edit_confirm_password_{user_key}")

            # حالة الحساب
            is_active = st.checkbox("الحساب نشط / Account Active", value=selected_user.get('is_active', True), key=f"edit_is_active_{user_key}")

        st.markdown("---")

        # الأدوار
        st.markdown("### 🎭 الأدوار / Roles")
        current_roles = selected_user.get('roles', [])

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            edit_is_admin = st.checkbox(f"🔐 {t('admin', lang)}", value='admin' in current_roles, key=f"edit_role_admin_{user_key}")
        with col2:
            edit_is_program_coord = st.checkbox(f"🏛️ {t('program_coordinator', lang)}", value='program_coordinator' in current_roles, key=f"edit_role_program_coord_{user_key}")
        with col3:
            edit_is_course_coord = st.checkbox(f"📚 {t('course_coordinator', lang)}", value='course_coordinator' in current_roles, key=f"edit_role_course_coord_{user_key}")
        with col4:
            edit_is_section_instructor = st.checkbox(f"👨‍🏫 {t('section_instructor', lang)}", value='section_instructor' in current_roles, key=f"edit_role_section_instructor_{user_key}")

        # البرامج
        edit_selected_programs = []
        if edit_is_program_coord:
            st.markdown("#### 🏛️ البرامج المعينة / Assigned Programs")
            if programs:
                program_options = {f"{p['program_code']} - {p['program_name_en']}": p['program_id'] for p in programs}
                current_program_keys = [k for k, v in program_options.items() if v in selected_user.get('assigned_programs', [])]
                edit_selected_program_keys = st.multiselect(
                    "اختر البرامج / Select Programs",
                    options=list(program_options.keys()),
                    default=current_program_keys,
                    key=f"edit_programs_select_{user_key}"
                )
                edit_selected_programs = [program_options[k] for k in edit_selected_program_keys]
            else:
                st.warning("⚠️ لا توجد برامج مسجلة / No programs found")

        # المقررات
        edit_selected_courses = []
        if edit_is_course_coord:
            st.markdown("#### 📚 المقررات المعينة / Assigned Courses")
            if courses:
                course_options = {f"{c['course_code']} - {c['course_title_en']}": c['course_id'] for c in courses}
                current_course_keys = [k for k, v in course_options.items() if v in selected_user.get('assigned_courses', [])]
                edit_selected_course_keys = st.multiselect(
                    "اختر المقررات / Select Courses",
                    options=list(course_options.keys()),
                    default=current_course_keys,
                    key=f"edit_courses_select_{user_key}"
                )
                edit_selected_courses = [course_options[k] for k in edit_selected_course_keys]
            else:
                st.warning("⚠️ لا توجد مقررات مسجلة / No courses found")

        # الشعب
        edit_selected_sections = {}
        if edit_is_section_instructor:
            st.markdown("#### 👨‍🏫 الشعب المعينة / Assigned Sections")

            # تجميع الشعب حسب المقرر
            sections_by_course = {}
            for sec in sections:
                course_id = sec.get('course_id')
                if course_id not in sections_by_course:
                    sections_by_course[course_id] = []
                sections_by_course[course_id].append(sec)

            # عرض الشعب
            section_options = {}
            for course_id, secs in sections_by_course.items():
                course = next((c for c in courses if c['course_id'] == course_id), None)
                if course:
                    course_code = course.get('course_code', course_id)
                    for sec in secs:
                        sec_num = sec.get('section_number', '')
                        semester = sec.get('semester_code', '')
                        year = sec.get('academic_year', '')
                        key = f"{course_code} - Section {sec_num} ({semester}/{year})"
                        section_options[key] = {'course_id': course_id, 'section_number': sec_num}

            # الحصول على الشعب الحالية
            current_section_keys = []
            current_sections = selected_user.get('assigned_sections', {})
            for course_id, sec_nums in current_sections.items():
                course = next((c for c in courses if c['course_id'] == course_id), None)
                if course:
                    course_code = course.get('course_code', course_id)
                    for sec_num in sec_nums:
                        for key, val in section_options.items():
                            if val['course_id'] == course_id and val['section_number'] == sec_num:
                                current_section_keys.append(key)

            if section_options:
                edit_selected_section_keys = st.multiselect(
                    "اختر الشعب / Select Sections",
                    options=list(section_options.keys()),
                    default=current_section_keys,
                    key=f"edit_sections_select_{user_key}"
                )

                # تجميع الشعب المختارة
                for key in edit_selected_section_keys:
                    sec_info = section_options[key]
                    course_id = sec_info['course_id']
                    sec_num = sec_info['section_number']
                    if course_id not in edit_selected_sections:
                        edit_selected_sections[course_id] = []
                    edit_selected_sections[course_id].append(sec_num)
            else:
                st.warning("⚠️ لا توجد شعب مسجلة / No sections found")

        st.markdown("---")

        # أزرار الإجراءات
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 حفظ التغييرات / Save Changes", type="primary", use_container_width=True, key=f"save_user_changes_{user_key}"):
                # التحقق من الأدوار
                new_roles = []
                if edit_is_admin:
                    new_roles.append("admin")
                if edit_is_program_coord:
                    new_roles.append("program_coordinator")
                if edit_is_course_coord:
                    new_roles.append("course_coordinator")
                if edit_is_section_instructor:
                    new_roles.append("section_instructor")

                if not new_roles:
                    st.error("⚠️ يرجى اختيار دور واحد على الأقل / Please select at least one role")
                    return

                # التحقق من كلمة المرور إذا تم تغييرها
                if change_password:
                    if not new_password:
                        st.error("⚠️ يرجى إدخال كلمة المرور الجديدة / Please enter new password")
                        return
                    if new_password != confirm_new_password:
                        st.error("⚠️ كلمات المرور غير متطابقة / Passwords do not match")
                        return

                # تحديث البيانات
                for u in users:
                    if u.get('user_id') == selected_user.get('user_id'):
                        u['full_name'] = new_full_name
                        u['email'] = new_email
                        u['roles'] = new_roles
                        u['is_active'] = is_active
                        u['assigned_programs'] = edit_selected_programs if edit_is_program_coord else []
                        u['assigned_courses'] = edit_selected_courses if edit_is_course_coord else []
                        u['assigned_sections'] = edit_selected_sections if edit_is_section_instructor else {}

                        if change_password:
                            u['password_hash'] = hashlib.sha256(new_password.encode()).hexdigest()
                        break

                # حفظ الملف
                with open(db.users_file, 'w', encoding='utf-8') as f:
                    json.dump({"users": users, "last_updated": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)

                st.success("✅ تم حفظ التغييرات بنجاح / Changes saved successfully")
                st.rerun()

        with col2:
            # إعادة تعيين كلمة المرور
            if st.button("🔄 إعادة تعيين كلمة المرور / Reset Password", use_container_width=True, key=f"reset_password_{user_key}"):
                new_auto_password = generate_password()

                for u in users:
                    if u.get('user_id') == selected_user.get('user_id'):
                        u['password_hash'] = hashlib.sha256(new_auto_password.encode()).hexdigest()
                        break

                with open(db.users_file, 'w', encoding='utf-8') as f:
                    json.dump({"users": users, "last_updated": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)

                st.success(f"✅ تم إعادة تعيين كلمة المرور / Password reset successfully")
                st.info(f"🔑 كلمة المرور الجديدة / New password: **{new_auto_password}**")

        with col3:
            # حذف المستخدم
            if selected_user.get('username') != 'admin':  # لا يمكن حذف المدير
                if st.button("🗑️ حذف المستخدم / Delete User", type="secondary", use_container_width=True, key=f"delete_user_{user_key}"):
                    st.session_state.confirm_delete_user = selected_user.get('user_id')
            else:
                st.button("🗑️ حذف المستخدم / Delete User", disabled=True, use_container_width=True, key=f"delete_user_disabled_{user_key}")
                st.caption("⚠️ لا يمكن حذف حساب المدير / Cannot delete admin account")

        # تأكيد الحذف
        if hasattr(st.session_state, 'confirm_delete_user') and st.session_state.confirm_delete_user == selected_user.get('user_id'):
            st.warning("⚠️ هل أنت متأكد من حذف هذا المستخدم؟ / Are you sure you want to delete this user?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ نعم، احذف / Yes, Delete", type="primary", use_container_width=True, key=f"confirm_delete_{user_key}"):
                    users = [u for u in users if u.get('user_id') != selected_user.get('user_id')]

                    with open(db.users_file, 'w', encoding='utf-8') as f:
                        json.dump({"users": users, "last_updated": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)

                    del st.session_state.confirm_delete_user
                    st.success("✅ تم حذف المستخدم بنجاح / User deleted successfully")
                    st.rerun()
            with col2:
                if st.button("❌ إلغاء / Cancel", use_container_width=True, key=f"cancel_delete_{user_key}"):
                    del st.session_state.confirm_delete_user
                    st.rerun()

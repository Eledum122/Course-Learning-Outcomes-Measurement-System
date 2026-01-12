"""
صفحة إدارة المقررات
Courses Management Page
"""

import streamlit as st
import pandas as pd
from models.database import Database, UserRole
from translations import t


def show_courses_management(db: Database, user, lang: str):
    """عرض صفحة إدارة المقررات"""

    is_rtl = lang == 'ar'

    st.title(f"📚 {t('courses_management', lang)}")

    # التحقق من الصلاحيات - يسمح للمديرين ومنسقي البرامج ومنسقي المقررات
    if user.role not in [UserRole.ADMIN, UserRole.PROGRAM_COORDINATOR, UserRole.COURSE_COORDINATOR]:
        st.error(f"⛔ {t('no_permission', lang)}")
        return

    # علامات التبويب
    tab1, tab2 = st.tabs([
        f"📋 {t('courses_list', lang)}",
        f"➕ {t('new_course', lang)}"
    ])

    # علامة التبويب الأولى: قائمة المقررات
    with tab1:
        show_courses_list(db, user, lang, is_rtl)

    # علامة التبويب الثانية: إضافة مقرر
    with tab2:
        show_add_course_form(db, lang, is_rtl)


def show_courses_list(db: Database, user, lang: str, is_rtl: bool):
    """عرض قائمة المقررات"""

    st.subheader(f"📋 {t('courses_list', lang)}")

    # فلتر حسب البرنامج
    programs = db.get_all_programs()

    if not programs:
        st.warning(f"⚠️ {t('no_programs_found', lang)}")
        st.info(f"ℹ️ {t('add_program_first', lang)}")
        return

    # إنشاء خيارات البرامج
    program_options = {t('all', lang): "all"}
    program_options.update({
        p.get('program_name_ar' if lang == 'ar' else 'program_name_en', ''): p.get('program_id')
        for p in programs
    })

    selected_program_name = st.selectbox(
        f"🏛️ {t('filter_by_program', lang)}",
        options=list(program_options.keys()),
        key='filter_program'
    )

    selected_program_id = program_options[selected_program_name]

    # تحميل المقررات
    if selected_program_id == "all":
        courses = db.get_all_courses()
    else:
        courses = db.get_courses_by_program(selected_program_id)

    if not courses:
        st.info(f"ℹ️ {t('no_data', lang)}")
        return

    # تحويل إلى DataFrame
    courses_data = []
    programs_dict = {p.get('program_id'): p.get('program_name_ar' if lang == 'ar' else 'program_name_en', '')
                     for p in programs}
    users_dict = {u.user_id: u.full_name for u in db.get_all_users()}

    for course in courses:
        course_title = course.get('course_title_ar' if lang == 'ar' else 'course_title_en', '')
        program_name = programs_dict.get(course.get('program_id', ''), t('not_specified', lang))
        coordinator_name = users_dict.get(course.get('coordinator_id', ''), t('not_specified', lang))
        status_text = t('active', lang) if course.get('is_active', True) else t('inactive', lang)

        courses_data.append({
            t('course_code', lang): course.get('course_code', ''),
            t('course_title', lang): course_title,
            t('program', lang): program_name,
            t('credit_hours', lang): course.get('credit_hours', 0),
            t('course_coordinator', lang): coordinator_name,
            t('status', lang): status_text
        })

    df = pd.DataFrame(courses_data)

    # عرض الجدول
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # قسم تعديل/حذف المقرر
    st.subheader(f"✏️ {t('edit_delete_course', lang)}")

    col1, col2 = st.columns([3, 1])

    with col1:
        # اختيار مقرر للتعديل
        course_options = {
            f"{c.get('course_code', '')} - {c.get('course_title_ar' if lang == 'ar' else 'course_title_en', '')}": c
            for c in courses
        }

        if course_options:
            selected_course_name = st.selectbox(
                t('select_course', lang),
                options=list(course_options.keys()),
                key='edit_course_select'
            )
        else:
            st.info(f"ℹ️ {t('no_courses_available', lang)}")
            return

    with col2:
        st.write("")
        st.write("")
        delete_btn = st.button(
            f"🗑️ {t('delete', lang)}",
            type='secondary',
            use_container_width=True,
            key='delete_course_btn'
        )

    if selected_course_name and selected_course_name in course_options:
        selected_course = course_options[selected_course_name]

        # نموذج التعديل
        with st.form(key='edit_course_form'):
            st.markdown(f"### ✏️ {t('edit_course', lang)}: {selected_course.get('course_code', '')}")

            col1, col2 = st.columns(2)

            with col1:
                course_title_ar = st.text_input(
                    t('course_title_ar', lang) + " *",
                    value=selected_course.get('course_title_ar', ''),
                    key='edit_course_title_ar'
                )

            with col2:
                course_title_en = st.text_input(
                    t('course_title_en', lang) + " *",
                    value=selected_course.get('course_title_en', ''),
                    key='edit_course_title_en'
                )

            # البرنامج
            current_program_id = selected_course.get('program_id', '')
            program_select_options = {
                p.get('program_name_ar' if lang == 'ar' else 'program_name_en', ''): p.get('program_id')
                for p in programs
            }

            current_program_index = 0
            for idx, (name, pid) in enumerate(program_select_options.items()):
                if pid == current_program_id:
                    current_program_index = idx
                    break

            selected_program_for_edit = st.selectbox(
                f"🏛️ {t('program', lang)} *",
                options=list(program_select_options.keys()),
                index=current_program_index,
                key='edit_program'
            )
            new_program_id = program_select_options[selected_program_for_edit]

            col1, col2, col3 = st.columns(3)

            with col1:
                credit_hours = st.number_input(
                    t('credit_hours', lang),
                    min_value=0,
                    max_value=10,
                    value=selected_course.get('credit_hours', 3),
                    key='edit_credit_hours'
                )

            with col2:
                theory_hours = st.number_input(
                    t('theory_hours', lang),
                    min_value=0,
                    max_value=10,
                    value=selected_course.get('theory_hours', 3),
                    key='edit_theory_hours'
                )

            with col3:
                practical_hours = st.number_input(
                    t('practical_hours', lang),
                    min_value=0,
                    max_value=10,
                    value=selected_course.get('practical_hours', 0),
                    key='edit_practical_hours'
                )

            col1, col2 = st.columns(2)

            with col1:
                course_level = st.text_input(
                    t('course_level', lang),
                    value=selected_course.get('course_level', ''),
                    placeholder="5",
                    key='edit_course_level'
                )

            with col2:
                course_type = st.text_input(
                    t('course_type', lang),
                    value=selected_course.get('course_type', ''),
                    placeholder=t('required', lang) if lang == 'ar' else "Required",
                    key='edit_course_type'
                )

            prerequisites = st.text_input(
                t('prerequisites', lang),
                value=selected_course.get('prerequisites', ''),
                placeholder="CSC101, CSC102",
                key='edit_prerequisites'
            )

            # منسق المقرر
            st.markdown(f"**{t('course_coordinator', lang)}:**")

            # جلب المستخدمين الذين لديهم صلاحية منسق مقرر
            all_users = db.get_all_users()
            coordinators = [u for u in all_users if 'course_coordinator' in u.roles or 'admin' in u.roles]

            coordinator_options = {f"{u.full_name} ({u.username})": u.user_id for u in coordinators}
            coordinator_options["--- " + t('not_specified', lang) + " ---"] = ""

            current_coordinator = selected_course.get('coordinator_id', '')
            current_coord_index = 0
            if current_coordinator:
                for idx, (name, uid) in enumerate(coordinator_options.items()):
                    if uid == current_coordinator:
                        current_coord_index = idx
                        break

            selected_coordinator_name = st.selectbox(
                t('select_coordinator', lang),
                options=list(coordinator_options.keys()),
                index=current_coord_index,
                key='edit_coordinator'
            )

            new_coordinator_id = coordinator_options[selected_coordinator_name]

            # الوصف
            col1, col2 = st.columns(2)
            with col1:
                description_ar = st.text_area(
                    t('description_ar', lang),
                    value=selected_course.get('description_ar', ''),
                    height=100,
                    key='edit_description_ar'
                )

            with col2:
                description_en = st.text_area(
                    t('description_en', lang),
                    value=selected_course.get('description_en', ''),
                    height=100,
                    key='edit_description_en'
                )

            # حالة المقرر
            is_active = st.checkbox(
                t('active', lang),
                value=selected_course.get('is_active', True),
                key='edit_is_active'
            )

            # زر الحفظ
            submit_btn = st.form_submit_button(
                f"💾 {t('save_changes', lang)}",
                type='primary',
                use_container_width=True
            )

            if submit_btn:
                # التحقق من الحقول المطلوبة
                if not course_title_ar or not course_title_en:
                    st.error(f"⚠️ {t('please_fill_required_fields', lang)}")
                else:
                    # تحديث المقرر
                    success = db.update_course(
                        course_id=selected_course.get('course_id'),
                        course_title_ar=course_title_ar,
                        course_title_en=course_title_en,
                        program_id=new_program_id,
                        credit_hours=credit_hours,
                        theory_hours=theory_hours,
                        practical_hours=practical_hours,
                        course_level=course_level,
                        prerequisites=prerequisites,
                        course_type=course_type,
                        description_ar=description_ar,
                        description_en=description_en,
                        coordinator_id=new_coordinator_id,
                        is_active=is_active
                    )

                    if success:
                        st.success(f"✅ {t('course_updated_successfully', lang)}")
                        st.rerun()
                    else:
                        st.error(f"❌ {t('course_update_failed', lang)}")

        # حذف المقرر
        if delete_btn:
            # تأكيد الحذف
            with st.expander(f"⚠️ {t('confirm_delete', lang)}", expanded=True):
                st.warning(t('confirm_delete_course', lang))

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ {t('yes_delete', lang)}", type='primary', use_container_width=True):
                        success = db.delete_course(selected_course.get('course_id'))
                        if success:
                            st.success(f"✅ {t('course_deleted_successfully', lang)}")
                            st.rerun()
                        else:
                            st.error(f"❌ {t('course_delete_failed', lang)}")

                with col2:
                    if st.button(f"❌ {t('cancel', lang)}", use_container_width=True):
                        st.rerun()


def show_add_course_form(db: Database, lang: str, is_rtl: bool):
    """عرض نموذج إضافة مقرر جديد"""

    st.subheader(f"➕ {t('new_course', lang)}")

    # التحقق من وجود برامج
    programs = db.get_all_programs()

    if not programs:
        st.warning(f"⚠️ {t('no_programs_found', lang)}")
        st.info(f"ℹ️ {t('add_program_first', lang)}")
        return

    with st.form(key='add_course_form'):
        # رمز المقرر
        course_code = st.text_input(
            t('course_code', lang) + " *",
            placeholder="CSC101",
            key='new_course_code'
        )

        col1, col2 = st.columns(2)

        with col1:
            course_title_ar = st.text_input(
                t('course_title_ar', lang) + " *",
                placeholder="مقدمة في علوم الحاسب",
                key='new_course_title_ar'
            )

        with col2:
            course_title_en = st.text_input(
                t('course_title_en', lang) + " *",
                placeholder="Introduction to Computer Science",
                key='new_course_title_en'
            )

        # البرنامج
        program_options = {
            p.get('program_name_ar' if lang == 'ar' else 'program_name_en', ''): p.get('program_id')
            for p in programs
        }

        selected_program = st.selectbox(
            f"🏛️ {t('program', lang)} *",
            options=list(program_options.keys()),
            key='new_program'
        )
        program_id = program_options[selected_program]

        col1, col2, col3 = st.columns(3)

        with col1:
            credit_hours = st.number_input(
                t('credit_hours', lang) + " *",
                min_value=1,
                max_value=10,
                value=3,
                key='new_credit_hours'
            )

        with col2:
            theory_hours = st.number_input(
                t('theory_hours', lang) + " *",
                min_value=0,
                max_value=10,
                value=3,
                key='new_theory_hours'
            )

        with col3:
            practical_hours = st.number_input(
                t('practical_hours', lang),
                min_value=0,
                max_value=10,
                value=0,
                key='new_practical_hours'
            )

        col1, col2 = st.columns(2)

        with col1:
            course_level = st.text_input(
                t('course_level', lang),
                placeholder="5",
                key='new_course_level'
            )

        with col2:
            course_type = st.text_input(
                t('course_type', lang),
                placeholder=t('required', lang) if lang == 'ar' else "Required",
                key='new_course_type'
            )

        prerequisites = st.text_input(
            t('prerequisites', lang),
            placeholder="CSC101, CSC102",
            key='new_prerequisites'
        )

        # منسق المقرر
        st.markdown(f"**{t('course_coordinator', lang)}:**")

        # جلب المستخدمين الذين لديهم صلاحية منسق مقرر
        all_users = db.get_all_users()
        coordinators = [u for u in all_users if 'course_coordinator' in u.roles or 'admin' in u.roles]

        coordinator_options = {f"{u.full_name} ({u.username})": u.user_id for u in coordinators}
        coordinator_options["--- " + t('not_specified', lang) + " ---"] = ""

        selected_coordinator_name = st.selectbox(
            t('select_coordinator', lang),
            options=list(coordinator_options.keys()),
            key='new_coordinator'
        )

        coordinator_id = coordinator_options[selected_coordinator_name]

        # الوصف
        col1, col2 = st.columns(2)
        with col1:
            description_ar = st.text_area(
                t('description_ar', lang),
                placeholder="وصف المقرر بالعربية...",
                height=100,
                key='new_description_ar'
            )

        with col2:
            description_en = st.text_area(
                t('description_en', lang),
                placeholder="Course description in English...",
                height=100,
                key='new_description_en'
            )

        st.markdown(f"<p style='color: #666; font-size: 12px;'>* {t('required_fields', lang)}</p>",
                   unsafe_allow_html=True)

        # زر الإضافة
        submit_btn = st.form_submit_button(
            f"➕ {t('add_course', lang)}",
            type='primary',
            use_container_width=True
        )

        if submit_btn:
            # التحقق من الحقول المطلوبة
            if not course_code or not course_title_ar or not course_title_en:
                st.error(f"⚠️ {t('please_fill_required_fields', lang)}")
            else:
                # إضافة المقرر
                success = db.add_course(
                    course_code=course_code,
                    course_title_ar=course_title_ar,
                    course_title_en=course_title_en,
                    program_id=program_id,
                    credit_hours=credit_hours,
                    theory_hours=theory_hours,
                    practical_hours=practical_hours,
                    course_level=course_level or "",
                    prerequisites=prerequisites or "",
                    course_type=course_type or "",
                    description_ar=description_ar or "",
                    description_en=description_en or "",
                    coordinator_id=coordinator_id or ""
                )

                if success:
                    st.success(f"✅ {t('course_added_successfully', lang)}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {t('course_code_exists', lang)}")

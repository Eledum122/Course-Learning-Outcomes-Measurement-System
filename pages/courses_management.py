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

    # إعادة بناء كائن المستخدم من قاعدة البيانات لضمان صحة الأدوار
    user = db.get_user_by_username(user.username)
    if not user:
        st.error("⛔ خطأ في تحميل بيانات المستخدم")
        return

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

    # عرض رسائل النجاح إذا كانت موجودة
    if st.session_state.get('course_delete_success'):
        course_code = st.session_state.get('course_delete_code', '')
        st.success(f"✅ تم حذف المقرر ({course_code}) بنجاح / Course ({course_code}) deleted successfully")
        st.session_state['course_delete_success'] = False
        st.session_state['course_delete_code'] = ''

    # تحميل جميع البرامج
    all_programs = db.get_all_programs()

    # تصفية البرامج حسب الصلاحيات
    if user.role == UserRole.PROGRAM_COORDINATOR:
        # منسق البرنامج يرى فقط برامجه
        user_data = db.load_users()
        assigned_programs = []
        for u in user_data:
            if u.get('user_id') == user.user_id:
                assigned_programs = u.get('assigned_programs', [])
                break
        programs = [p for p in all_programs if p.get('program_id') in assigned_programs]
    elif user.role == UserRole.COURSE_COORDINATOR:
        # منسق المقرر يرى مقرراته فقط (سنصفي المقررات لاحقاً)
        programs = all_programs
    else:
        # المدير يرى جميع البرامج
        programs = all_programs

    if not programs:
        if user.role == UserRole.PROGRAM_COORDINATOR:
            st.warning(f"⚠️ {t('no_programs_assigned', lang) if lang == 'ar' else 'No programs assigned to you'}")
        else:
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
        all_courses = db.get_all_courses()
    else:
        all_courses = db.get_courses_by_program(selected_program_id)

    # تصفية المقررات حسب الصلاحيات
    if user.role == UserRole.COURSE_COORDINATOR:
        # منسق المقرر يرى فقط مقرراته
        user_data = db.load_users()
        assigned_courses = []
        for u in user_data:
            if u.get('user_id') == user.user_id:
                assigned_courses = u.get('assigned_courses', [])
                break
        # تصفية المقررات: إما مُسندة له في assigned_courses أو coordinator_id يساوي user_id
        courses = [c for c in all_courses
                  if c.get('course_id') in assigned_courses or c.get('coordinator_id') == user.user_id]
    elif user.role == UserRole.PROGRAM_COORDINATOR:
        # منسق البرنامج يرى مقررات برامجه فقط
        if selected_program_id == "all":
            user_data = db.load_users()
            assigned_programs = []
            for u in user_data:
                if u.get('user_id') == user.user_id:
                    assigned_programs = u.get('assigned_programs', [])
                    break
            courses = [c for c in all_courses if c.get('program_id') in assigned_programs]
        else:
            courses = all_courses
    else:
        # المدير يرى جميع المقررات
        courses = all_courses

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
            "الإصدار / Version": course.get('course_version', '-'),
            t('course_coordinator', lang): coordinator_name,
            t('status', lang): status_text
        })

    df = pd.DataFrame(courses_data)

    # عرض الجدول
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # قسم تعديل/حذف المقرر
    st.subheader(f"✏️ {t('edit_delete_course', lang)}")

    # اختيار مقرر للتعديل - خارج النموذج
    course_list = [(f"{c.get('course_code', '')} - {c.get('course_title_ar' if lang == 'ar' else 'course_title_en', '')}", c) for c in courses]
    course_names = [name for name, _ in course_list]

    if not course_names:
        st.info(f"ℹ️ {t('no_courses_available', lang)}")
        return

    col1, col2 = st.columns([3, 1])

    # تتبع المقرر المحدد السابق
    if 'previous_selected_course' not in st.session_state:
        st.session_state.previous_selected_course = course_names[0] if course_names else None

    with col1:
        selected_course_name = st.selectbox(
            t('select_course', lang),
            options=course_names,
            key='edit_course_select_main'
        )

    # التحقق من تغيير المقرر المختار
    if selected_course_name != st.session_state.previous_selected_course:
        st.session_state.previous_selected_course = selected_course_name
        st.rerun()

    # الحصول على المقرر المحدد
    selected_course = next((c for name, c in course_list if name == selected_course_name), None)

    if not selected_course:
        st.error("❌ خطأ في تحميل المقرر")
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

    # نموذج التعديل - استخدام key ديناميكي لإعادة إنشاء النموذج عند تغيير المقرر
    course_id = selected_course.get("course_id")
    with st.form(key=f'edit_course_form_{course_id}'):
        st.markdown(f"### ✏️ {t('edit_course', lang)}: {selected_course.get('course_code', '')}")

        col1, col2 = st.columns(2)

        with col1:
            course_title_ar = st.text_input(
                t('course_title_ar', lang) + " *",
                value=selected_course.get('course_title_ar', ''),
                key=f'edit_course_title_ar_{course_id}'
            )

        with col2:
            course_title_en = st.text_input(
                t('course_title_en', lang) + " *",
                value=selected_course.get('course_title_en', ''),
                key=f'edit_course_title_en_{course_id}'
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
            key=f'edit_program_{course_id}'
        )
        new_program_id = program_select_options[selected_program_for_edit]

        col1, col2, col3 = st.columns(3)

        with col1:
            credit_hours = st.number_input(
                t('credit_hours', lang),
                min_value=0,
                max_value=10,
                value=selected_course.get('credit_hours', 3),
                key=f'edit_credit_hours_{course_id}'
            )

        with col2:
            theory_hours = st.number_input(
                t('theory_hours', lang),
                min_value=0,
                max_value=10,
                value=selected_course.get('theory_hours', 3),
                key=f'edit_theory_hours_{course_id}'
            )

        with col3:
            practical_hours = st.number_input(
                t('practical_hours', lang),
                min_value=0,
                max_value=10,
                value=selected_course.get('practical_hours', 0),
                key=f'edit_practical_hours_{course_id}'
            )

        col1, col2, col3 = st.columns(3)

        with col1:
            course_level = st.text_input(
                t('course_level', lang),
                value=selected_course.get('course_level', ''),
                placeholder="5",
                key=f'edit_course_level_{course_id}'
            )

        with col2:
            course_type = st.text_input(
                t('course_type', lang),
                value=selected_course.get('course_type', ''),
                placeholder=t('required', lang) if lang == 'ar' else "Required",
                key=f'edit_course_type_{course_id}'
            )

        with col3:
            course_version = st.text_input(
                "إصدار المقرر / Course Version",
                value=selected_course.get('course_version', ''),
                placeholder="1.0",
                key=f'edit_course_version_{course_id}'
            )

        prerequisites = st.text_input(
            t('prerequisites', lang),
            value=selected_course.get('prerequisites', ''),
            placeholder="CSC101, CSC102",
            key=f'edit_prerequisites_{course_id}'
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
            key=f'edit_coordinator_{course_id}'
        )

        new_coordinator_id = coordinator_options[selected_coordinator_name]

        # الوصف
        col1, col2 = st.columns(2)
        with col1:
            description_ar = st.text_area(
                t('description_ar', lang),
                value=selected_course.get('description_ar', ''),
                height=100,
                key=f'edit_description_ar_{course_id}'
            )

        with col2:
            description_en = st.text_area(
                t('description_en', lang),
                value=selected_course.get('description_en', ''),
                height=100,
                key=f'edit_description_en_{course_id}'
            )

        # حالة المقرر
        is_active = st.checkbox(
            t('active', lang),
            value=selected_course.get('is_active', True),
            key=f'edit_is_active_{course_id}'
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
                    is_active=is_active,
                    course_version=course_version
                )

                if success:
                    st.success(f"✅ {t('course_updated_successfully', lang)}")
                    st.rerun()
                else:
                    st.error(f"❌ {t('course_update_failed', lang)}")

    # حذف المقرر
    if delete_btn:
        st.session_state['show_course_delete_confirmation'] = True
        st.session_state['course_to_delete'] = selected_course
        st.rerun()

    # عرض نافذة تأكيد الحذف
    if st.session_state.get('show_course_delete_confirmation') and st.session_state.get('course_to_delete'):
        course_to_delete = st.session_state['course_to_delete']
        st.markdown("---")
        st.warning(f"⚠️ هل أنت متأكد من حذف المقرر **{course_to_delete.get('course_code')}**؟")
        st.info(f"ℹ️ سيتم حذف جميع البيانات المرتبطة بهذا المقرر بما في ذلك CLOs.")

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button(f"✅ نعم، احذف المقرر", type='primary', use_container_width=True, key='confirm_delete_course_btn'):
                success = db.delete_course(course_to_delete.get('course_id'))
                if success:
                    st.session_state['course_delete_success'] = True
                    st.session_state['course_delete_code'] = course_to_delete.get('course_code')
                    st.session_state['show_course_delete_confirmation'] = False
                    st.session_state['course_to_delete'] = None
                    st.rerun()
                else:
                    st.error(f"❌ {t('course_delete_failed', lang)}")
                    st.session_state['show_course_delete_confirmation'] = False
                    st.session_state['course_to_delete'] = None

        with col2:
            if st.button(f"❌ إلغاء", use_container_width=True, key='cancel_delete_course_btn'):
                st.session_state['show_course_delete_confirmation'] = False
                st.session_state['course_to_delete'] = None
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

        col1, col2, col3 = st.columns(3)

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

        with col3:
            course_version = st.text_input(
                "إصدار المقرر / Course Version",
                placeholder="1.0",
                key='new_course_version'
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
                    coordinator_id=coordinator_id or "",
                    course_version=course_version or ""
                )

                if success:
                    st.success(f"✅ {t('course_added_successfully', lang)}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {t('course_code_exists', lang)}")

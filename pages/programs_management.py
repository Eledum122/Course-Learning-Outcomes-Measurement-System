"""
صفحة إدارة البرامج الأكاديمية
Academic Programs Management Page
"""

import streamlit as st
import pandas as pd
from models.database import Database, UserRole
from translations import t
from pages.plos_management_section import show_plos_management


def show_programs_management(db: Database, user, lang: str):
    """عرض صفحة إدارة البرامج الأكاديمية"""

    # إعادة بناء كائن المستخدم من قاعدة البيانات لضمان صحة الأدوار
    user = db.get_user_by_username(user.username)
    if not user:
        st.error("⛔ خطأ في تحميل بيانات المستخدم")
        return

    is_rtl = lang == 'ar'

    st.title(f"🏛️ {t('academic_programs_management', lang)}")

    # التحقق من الصلاحيات - يسمح للمديرين ومنسقي البرامج
    if user.role not in [UserRole.ADMIN, UserRole.PROGRAM_COORDINATOR]:
        st.error(f"⛔ {t('no_permission', lang)}")
        return

    # تحميل البرامج للاستخدام في التبويبات
    all_programs = db.get_all_programs()

    # تصفية البرامج حسب الصلاحيات
    if user.role == UserRole.PROGRAM_COORDINATOR:
        user_data = db.load_users()
        assigned_programs = []
        for u in user_data:
            if u.get('user_id') == user.user_id:
                assigned_programs = u.get('assigned_programs', [])
                break
        programs = [p for p in all_programs if p.get('program_id') in assigned_programs]
    else:
        programs = all_programs

    # علامات التبويب
    tab1, tab2, tab3 = st.tabs([
        f"📋 {t('programs_list', lang)}",
        f"➕ {t('new_program', lang)}",
        f"🎯 مخرجات البرنامج وطرق القياس"
    ])

    # علامة التبويب الأولى: قائمة البرامج
    with tab1:
        show_programs_list(db, user, lang, is_rtl)

    # علامة التبويب الثانية: إضافة برنامج
    with tab2:
        show_add_program_form(db, lang, is_rtl)

    # علامة التبويب الثالثة: إدارة PLOs وطرق القياس
    with tab3:
        show_plos_management(db, user, programs, lang, is_rtl)


def show_programs_list(db: Database, user, lang: str, is_rtl: bool):
    """عرض قائمة البرامج الأكاديمية"""

    st.subheader(f"📋 {t('programs_list', lang)}")

    # عرض رسائل النجاح إذا كانت موجودة
    if st.session_state.get('program_delete_success'):
        program_code = st.session_state.get('program_delete_code', '')
        st.success(f"✅ تم حذف البرنامج ({program_code}) بنجاح / Program ({program_code}) deleted successfully")
        st.session_state['program_delete_success'] = False
        st.session_state['program_delete_code'] = ''

    if st.session_state.get('program_update_success'):
        program_code = st.session_state.get('program_update_code', '')
        st.success(f"✅ تم تحديث البرنامج ({program_code}) بنجاح / Program ({program_code}) updated successfully")
        st.session_state['program_update_success'] = False
        st.session_state['program_update_code'] = ''

    # تحميل البرامج
    all_programs = db.get_all_programs()

    # تصفية البرامج حسب الصلاحيات
    if user.role == UserRole.PROGRAM_COORDINATOR:
        # منسق البرنامج يرى فقط البرامج المعينة له
        user_data = db.load_users()
        assigned_programs = []
        for u in user_data:
            if u.get('user_id') == user.user_id:
                assigned_programs = u.get('assigned_programs', [])
                break

        programs = [p for p in all_programs if p.get('program_id') in assigned_programs]
    else:
        # المدير يرى جميع البرامج
        programs = all_programs

    if not programs:
        if user.role == UserRole.PROGRAM_COORDINATOR:
            st.info(f"ℹ️ {t('no_assigned_programs', lang) if lang == 'ar' else 'No programs assigned to you yet'}")
        else:
            st.info(f"ℹ️ {t('no_data', lang)}")
        return

    # تحويل إلى DataFrame
    programs_data = []
    users_dict = {u.user_id: u.full_name for u in db.get_all_users()}

    for program in programs:
        program_name = program.get('program_name_ar' if lang == 'ar' else 'program_name_en', '')
        coordinator_name = users_dict.get(program.get('coordinator_id', ''), t('not_specified', lang))
        status_text = t('active', lang) if program.get('is_active', True) else t('inactive', lang)

        programs_data.append({
            t('program_code', lang): program.get('program_code', ''),
            t('program_name', lang): program_name,
            t('program_coordinator', lang): coordinator_name,
            t('status', lang): status_text
        })

    df = pd.DataFrame(programs_data)

    # عرض الجدول
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # قسم تعديل/حذف البرنامج
    st.subheader(f"✏️ تعديل/حذف برنامج / Edit/Delete Program")

    # اختيار برنامج للتعديل - خارج النموذج لتحديث البيانات عند التغيير
    program_list = [(f"{p.get('program_code', '')} - {p.get('program_name_ar' if lang == 'ar' else 'program_name_en', '')}", p) for p in programs]
    program_names = [name for name, _ in program_list]

    col1, col2 = st.columns([3, 1])

    # تتبع البرنامج المحدد السابق
    if 'previous_selected_program' not in st.session_state:
        st.session_state.previous_selected_program = program_names[0] if program_names else None

    with col1:
        selected_program_name = st.selectbox(
            t('please_select_program', lang),
            options=program_names,
            key='edit_program_select_main'
        )

    # التحقق من تغيير البرنامج المختار
    if selected_program_name != st.session_state.previous_selected_program:
        st.session_state.previous_selected_program = selected_program_name
        st.rerun()

    # الحصول على البرنامج المحدد
    selected_program = next((p for name, p in program_list if name == selected_program_name), None)

    if not selected_program:
        st.error("❌ خطأ في تحميل البرنامج")
        return

    with col2:
        st.write("")
        st.write("")
        delete_btn = st.button(
            f"🗑️ {t('delete', lang)}",
            type='secondary',
            use_container_width=True,
            key='delete_program_btn'
        )

    # نموذج التعديل - استخدام key ديناميكي لإعادة إنشاء النموذج عند تغيير البرنامج
    program_id = selected_program.get("program_id")
    with st.form(key=f'edit_program_form_{program_id}'):
        st.markdown(f"### ✏️ {t('edit_program', lang)}: {selected_program.get('program_code', '')}")

        col1, col2 = st.columns(2)

        with col1:
            program_name_ar = st.text_input(
                t('program_name_ar', lang),
                value=selected_program.get('program_name_ar', ''),
                key=f'edit_program_name_ar_{program_id}'
            )

            university_ar = st.text_input(
                t('university_ar', lang),
                value=selected_program.get('university_ar', ''),
                key=f'edit_university_ar_{program_id}'
            )

            college_ar = st.text_input(
                t('college_ar', lang),
                value=selected_program.get('college_ar', ''),
                key=f'edit_college_ar_{program_id}'
            )

            department_ar = st.text_input(
                t('department_ar', lang),
                value=selected_program.get('department_ar', ''),
                key=f'edit_department_ar_{program_id}'
            )

        with col2:
            program_name_en = st.text_input(
                t('program_name_en', lang),
                value=selected_program.get('program_name_en', ''),
                key=f'edit_program_name_en_{program_id}'
            )

            university_en = st.text_input(
                t('university_en', lang),
                value=selected_program.get('university_en', ''),
                key=f'edit_university_en_{program_id}'
            )

            college_en = st.text_input(
                t('college_en', lang),
                value=selected_program.get('college_en', ''),
                key=f'edit_college_en_{program_id}'
            )

            department_en = st.text_input(
                t('department_en', lang),
                value=selected_program.get('department_en', ''),
                key=f'edit_department_en_{program_id}'
            )

            # منسق البرنامج
            st.markdown(f"**{t('program_coordinator', lang)}:**")

            # جلب المستخدمين الذين لديهم صلاحية منسق برنامج
            all_users = db.get_all_users()
            coordinators = [u for u in all_users if 'program_coordinator' in u.roles or 'admin' in u.roles]

            coordinator_options = {f"{u.full_name} ({u.username})": u.user_id for u in coordinators}
            coordinator_options["--- " + t('not_specified', lang) + " ---"] = ""

            current_coordinator = selected_program.get('coordinator_id', '')
            current_index = 0
            if current_coordinator:
                for idx, (name, uid) in enumerate(coordinator_options.items()):
                    if uid == current_coordinator:
                        current_index = idx
                        break

            selected_coordinator_name = st.selectbox(
                t('select_coordinator_for_program', lang),
                options=list(coordinator_options.keys()),
                index=current_index,
                key=f'edit_coordinator_{program_id}'
            )

            new_coordinator_id = coordinator_options[selected_coordinator_name]

        # الوصف
        col1, col2 = st.columns(2)
        with col1:
            description_ar = st.text_area(
                t('description_ar', lang),
                value=selected_program.get('description_ar', ''),
                height=100,
                key=f'edit_description_ar_{program_id}'
            )

        with col2:
            description_en = st.text_area(
                t('description_en', lang),
                value=selected_program.get('description_en', ''),
                height=100,
                key=f'edit_description_en_{program_id}'
            )

        # حالة البرنامج
        is_active = st.checkbox(
            t('active', lang),
            value=selected_program.get('is_active', True),
            key=f'edit_is_active_{program_id}'
        )

        # زر الحفظ
        submit_btn = st.form_submit_button(
            f"💾 {t('save_changes', lang)}",
            type='primary',
            use_container_width=True
        )

        if submit_btn:
            # التحقق من الحقول المطلوبة
            if not program_name_ar or not program_name_en:
                st.error(f"⚠️ {t('please_fill_required_fields', lang)}")
            else:
                # تحديث البرنامج
                success = db.update_program(
                    program_id=selected_program.get('program_id'),
                    program_name_ar=program_name_ar,
                    program_name_en=program_name_en,
                    university_ar=university_ar,
                    university_en=university_en,
                    college_ar=college_ar,
                    college_en=college_en,
                    department_ar=department_ar,
                    department_en=department_en,
                    description_ar=description_ar,
                    description_en=description_en,
                    coordinator_id=new_coordinator_id,
                    is_active=is_active
                )

                if success:
                    st.session_state['program_update_success'] = True
                    st.session_state['program_update_code'] = selected_program.get('program_code')
                    st.rerun()
                else:
                    st.error(f"❌ {t('program_update_failed', lang)}")

    # حذف البرنامج
    if delete_btn:
        st.session_state['show_delete_confirmation'] = True
        st.session_state['program_to_delete'] = selected_program
        st.rerun()

    # عرض نافذة تأكيد الحذف
    if st.session_state.get('show_delete_confirmation') and st.session_state.get('program_to_delete'):
        program_to_delete = st.session_state['program_to_delete']
        st.markdown("---")
        st.warning(f"⚠️ هل أنت متأكد من حذف البرنامج **{program_to_delete.get('program_code')}**؟")
        st.info(f"ℹ️ سيتم حذف جميع البيانات المرتبطة بهذا البرنامج بما في ذلك PLOs وطرق القياس.")

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button(f"✅ نعم، احذف البرنامج", type='primary', use_container_width=True, key='confirm_delete_btn'):
                success = db.delete_program(program_to_delete.get('program_id'))
                if success:
                    st.session_state['program_delete_success'] = True
                    st.session_state['program_delete_code'] = program_to_delete.get('program_code')
                    st.session_state['show_delete_confirmation'] = False
                    st.session_state['program_to_delete'] = None
                    st.rerun()
                else:
                    st.error(f"❌ {t('program_delete_failed', lang)}")
                    st.session_state['show_delete_confirmation'] = False
                    st.session_state['program_to_delete'] = None

        with col2:
            if st.button(f"❌ إلغاء", use_container_width=True, key='cancel_delete_btn'):
                st.session_state['show_delete_confirmation'] = False
                st.session_state['program_to_delete'] = None
                st.rerun()


def show_add_program_form(db: Database, lang: str, is_rtl: bool):
    """عرض نموذج إضافة برنامج جديد"""

    st.subheader(f"➕ {t('new_program', lang)}")

    with st.form(key='add_program_form'):
        # رمز البرنامج
        program_code = st.text_input(
            t('program_code', lang) + " *",
            placeholder="CS-BSc",
            key='new_program_code'
        )

        col1, col2 = st.columns(2)

        with col1:
            program_name_ar = st.text_input(
                t('program_name_ar', lang) + " *",
                placeholder="بكالوريوس علوم الحاسب",
                key='new_program_name_ar'
            )

            university_ar = st.text_input(
                t('university_ar', lang),
                placeholder="جامعة الملك سعود",
                key='new_university_ar'
            )

            college_ar = st.text_input(
                t('college_ar', lang),
                placeholder="كلية علوم الحاسب والمعلومات",
                key='new_college_ar'
            )

            department_ar = st.text_input(
                t('department_ar', lang),
                placeholder="قسم علوم الحاسب",
                key='new_department_ar'
            )

        with col2:
            program_name_en = st.text_input(
                t('program_name_en', lang) + " *",
                placeholder="Bachelor of Computer Science",
                key='new_program_name_en'
            )

            university_en = st.text_input(
                t('university_en', lang),
                placeholder="King Saud University",
                key='new_university_en'
            )

            college_en = st.text_input(
                t('college_en', lang),
                placeholder="College of Computer and Information Sciences",
                key='new_college_en'
            )

            department_en = st.text_input(
                t('department_en', lang),
                placeholder="Computer Science Department",
                key='new_department_en'
            )

        # منسق البرنامج
        st.markdown(f"**{t('program_coordinator', lang)}:**")

        # جلب المستخدمين الذين لديهم صلاحية منسق برنامج
        all_users = db.get_all_users()
        coordinators = [u for u in all_users if 'program_coordinator' in u.roles or 'admin' in u.roles]

        coordinator_options = {f"{u.full_name} ({u.username})": u.user_id for u in coordinators}
        coordinator_options["--- " + t('not_specified', lang) + " ---"] = ""

        selected_coordinator_name = st.selectbox(
            t('select_coordinator_for_program', lang),
            options=list(coordinator_options.keys()),
            key='new_coordinator'
        )

        coordinator_id = coordinator_options[selected_coordinator_name]

        # الوصف
        col1, col2 = st.columns(2)
        with col1:
            description_ar = st.text_area(
                t('description_ar', lang),
                placeholder="وصف البرنامج بالعربية...",
                height=100,
                key='new_description_ar'
            )

        with col2:
            description_en = st.text_area(
                t('description_en', lang),
                placeholder="Program description in English...",
                height=100,
                key='new_description_en'
            )

        st.markdown(f"<p style='color: #666; font-size: 12px;'>* {t('required_fields', lang)}</p>",
                   unsafe_allow_html=True)

        # زر الإضافة
        submit_btn = st.form_submit_button(
            f"➕ {t('new_program', lang)}",
            type='primary',
            use_container_width=True
        )

        if submit_btn:
            # التحقق من الحقول المطلوبة
            if not program_code or not program_name_ar or not program_name_en:
                st.error(f"⚠️ {t('please_fill_required_fields', lang)}")
            else:
                # إضافة البرنامج
                success = db.add_program(
                    program_code=program_code,
                    program_name_ar=program_name_ar,
                    program_name_en=program_name_en,
                    university_ar=university_ar or "",
                    university_en=university_en or "",
                    college_ar=college_ar or "",
                    college_en=college_en or "",
                    department_ar=department_ar or "",
                    department_en=department_en or "",
                    description_ar=description_ar or "",
                    description_en=description_en or "",
                    coordinator_id=coordinator_id or ""
                )

                if success:
                    st.success(f"✅ {t('program_created_success', lang)}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {t('program_create_failed', lang)}")


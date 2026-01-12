"""
صفحة إدارة المستخدمين
Users Management Page
"""

import streamlit as st
import pandas as pd
from models.database import Database, UserRole
from translations import t


def show_users_management(db: Database, user, lang: str):
    """عرض صفحة إدارة المستخدمين"""

    is_rtl = lang == 'ar'

    st.title(f"👥 {t('users_management', lang)}")

    # التحقق من الصلاحيات
    if user.role != UserRole.ADMIN:
        st.error(f"⛔ {t('no_permission', lang)}")
        return

    # علامات التبويب
    tab1, tab2 = st.tabs([
        f"📋 {t('users_list', lang)}",
        f"➕ {t('add_user', lang)}"
    ])

    # علامة التبويب الأولى: قائمة المستخدمين
    with tab1:
        show_users_list(db, lang, is_rtl)

    # علامة التبويب الثانية: إضافة مستخدم
    with tab2:
        show_add_user_form(db, lang, is_rtl)


def show_users_list(db: Database, lang: str, is_rtl: bool):
    """عرض قائمة المستخدمين"""

    st.subheader(f"📋 {t('users_list', lang)}")

    # تحميل المستخدمين
    users = db.get_all_users()

    if not users:
        st.info(f"ℹ️ {t('no_users_found', lang)}")
        return

    # تحويل إلى DataFrame
    users_data = []
    for user in users:
        roles_text = ", ".join([t(role, lang) for role in user.roles])
        status_text = t('active', lang) if getattr(user, 'is_active', True) else t('inactive', lang)

        users_data.append({
            t('user_id', lang): user.user_id,
            t('username', lang): user.username,
            t('full_name', lang): user.full_name,
            t('email', lang): user.email,
            t('employee_id', lang): user.employee_id,
            t('roles', lang): roles_text,
            t('status', lang): status_text
        })

    df = pd.DataFrame(users_data)

    # عرض الجدول
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # قسم تعديل/حذف المستخدم
    st.subheader(f"✏️ {t('edit_delete_user', lang)}")

    col1, col2 = st.columns([3, 1])

    with col1:
        # اختيار مستخدم للتعديل
        user_options = {f"{user.full_name} ({user.username})": user for user in users}
        selected_user_name = st.selectbox(
            t('select_user', lang),
            options=list(user_options.keys()),
            key='edit_user_select'
        )

    with col2:
        st.write("")
        st.write("")
        delete_btn = st.button(
            f"🗑️ {t('delete', lang)}",
            type='secondary',
            use_container_width=True,
            key='delete_user_btn'
        )

    if selected_user_name:
        selected_user = user_options[selected_user_name]

        # نموذج التعديل
        with st.form(key='edit_user_form'):
            st.markdown(f"### ✏️ {t('edit_user', lang)}: {selected_user.full_name}")

            col1, col2 = st.columns(2)

            with col1:
                full_name = st.text_input(
                    t('full_name', lang),
                    value=selected_user.full_name,
                    key='edit_full_name'
                )

                email = st.text_input(
                    t('email', lang),
                    value=selected_user.email,
                    key='edit_email'
                )

            with col2:
                employee_id = st.text_input(
                    t('employee_id', lang),
                    value=selected_user.employee_id,
                    key='edit_employee_id'
                )

                is_active = st.checkbox(
                    t('active', lang),
                    value=True,
                    key='edit_is_active'
                )

            # الأدوار
            st.markdown(f"**{t('roles', lang)}:**")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                role_admin = st.checkbox(
                    t('admin', lang),
                    value='admin' in selected_user.roles,
                    key='edit_role_admin'
                )

            with col2:
                role_program = st.checkbox(
                    t('program_coordinator', lang),
                    value='program_coordinator' in selected_user.roles,
                    key='edit_role_program'
                )

            with col3:
                role_course = st.checkbox(
                    t('course_coordinator', lang),
                    value='course_coordinator' in selected_user.roles,
                    key='edit_role_course'
                )

            with col4:
                role_instructor = st.checkbox(
                    t('section_instructor', lang),
                    value='section_instructor' in selected_user.roles,
                    key='edit_role_instructor'
                )

            # زر الحفظ
            submit_btn = st.form_submit_button(
                f"💾 {t('save_changes', lang)}",
                type='primary',
                use_container_width=True
            )

            if submit_btn:
                # جمع الأدوار المختارة
                new_roles = []
                if role_admin:
                    new_roles.append('admin')
                if role_program:
                    new_roles.append('program_coordinator')
                if role_course:
                    new_roles.append('course_coordinator')
                if role_instructor:
                    new_roles.append('section_instructor')

                # التحقق من وجود دور واحد على الأقل
                if not new_roles:
                    st.error(f"⚠️ {t('select_at_least_one_role', lang)}")
                else:
                    # تحديث المستخدم
                    success = db.update_user(
                        user_id=selected_user.user_id,
                        full_name=full_name,
                        email=email,
                        employee_id=employee_id,
                        roles=new_roles,
                        is_active=is_active
                    )

                    if success:
                        st.success(f"✅ {t('user_updated_successfully', lang)}")
                        st.rerun()
                    else:
                        st.error(f"❌ {t('failed_to_update_user', lang)}")

        # حذف المستخدم
        if delete_btn:
            # تأكيد الحذف
            with st.expander(f"⚠️ {t('confirm_delete', lang)}", expanded=True):
                st.warning(f"{t('confirm_delete_user_message', lang)}: **{selected_user.full_name}**")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ {t('yes_delete', lang)}", type='primary', use_container_width=True):
                        success = db.delete_user(selected_user.user_id)
                        if success:
                            st.success(f"✅ {t('user_deleted_successfully', lang)}")
                            st.rerun()
                        else:
                            st.error(f"❌ {t('failed_to_delete_user', lang)}")

                with col2:
                    if st.button(f"❌ {t('cancel', lang)}", use_container_width=True):
                        st.rerun()


def show_add_user_form(db: Database, lang: str, is_rtl: bool):
    """عرض نموذج إضافة مستخدم جديد"""

    st.subheader(f"➕ {t('add_new_user', lang)}")

    with st.form(key='add_user_form'):
        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input(
                t('username', lang) + " *",
                placeholder=t('enter_username', lang),
                key='new_username'
            )

            full_name = st.text_input(
                t('full_name', lang) + " *",
                placeholder=t('enter_full_name', lang),
                key='new_full_name'
            )

            email = st.text_input(
                t('email', lang),
                placeholder=t('enter_email', lang),
                key='new_email'
            )

        with col2:
            password = st.text_input(
                t('password', lang) + " *",
                type='password',
                placeholder=t('enter_password', lang),
                key='new_password'
            )

            confirm_password = st.text_input(
                t('confirm_password', lang) + " *",
                type='password',
                placeholder=t('enter_password_again', lang),
                key='new_confirm_password'
            )

            employee_id = st.text_input(
                t('employee_id', lang),
                placeholder=t('enter_employee_id', lang),
                key='new_employee_id'
            )

        # الأدوار
        st.markdown(f"**{t('select_roles', lang)}:** *")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            role_admin = st.checkbox(
                t('admin', lang),
                key='new_role_admin'
            )

        with col2:
            role_program = st.checkbox(
                t('program_coordinator', lang),
                key='new_role_program'
            )

        with col3:
            role_course = st.checkbox(
                t('course_coordinator', lang),
                key='new_role_course'
            )

        with col4:
            role_instructor = st.checkbox(
                t('section_instructor', lang),
                key='new_role_instructor'
            )

        st.markdown(f"<p style='color: #666; font-size: 12px;'>* {t('required_fields', lang)}</p>",
                   unsafe_allow_html=True)

        # زر الإضافة
        submit_btn = st.form_submit_button(
            f"➕ {t('add_user', lang)}",
            type='primary',
            use_container_width=True
        )

        if submit_btn:
            # التحقق من الحقول المطلوبة
            if not username or not password or not full_name:
                st.error(f"⚠️ {t('please_fill_required_fields', lang)}")
            elif password != confirm_password:
                st.error(f"⚠️ {t('passwords_do_not_match', lang)}")
            else:
                # جمع الأدوار
                roles = []
                if role_admin:
                    roles.append('admin')
                if role_program:
                    roles.append('program_coordinator')
                if role_course:
                    roles.append('course_coordinator')
                if role_instructor:
                    roles.append('section_instructor')

                if not roles:
                    st.error(f"⚠️ {t('select_at_least_one_role', lang)}")
                else:
                    # إضافة المستخدم
                    success = db.add_user(
                        username=username,
                        password=password,
                        full_name=full_name,
                        email=email or "",
                        roles=roles,
                        employee_id=employee_id or ""
                    )

                    if success:
                        st.success(f"✅ {t('user_added_successfully', lang)}")
                        st.balloons()
                        # مسح النموذج بإعادة تحميل الصفحة
                        st.rerun()
                    else:
                        st.error(f"❌ {t('username_already_exists', lang)}")

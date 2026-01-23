"""
صفحة إدارة مخرجات التعلم للمقررات (CLOs)
Course Learning Outcomes Management Page
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from models.database import Database, UserRole
from translations import t


def show_clos_management(db: Database, user, lang: str):
    """عرض صفحة إدارة مخرجات التعلم"""

    # إعادة بناء كائن المستخدم من قاعدة البيانات لضمان صحة الأدوار
    rebuilt_user = db.get_user_by_username(user.username)
    if not rebuilt_user:
        st.error("⛔ خطأ في تحميل بيانات المستخدم")
        return

    user = rebuilt_user
    is_rtl = lang == 'ar'

    st.title(f"📝 {t('clos_management', lang) if 'clos_management' in dir() else 'إدارة مخرجات التعلم / CLOs Management'}")

    # التحقق من الصلاحيات - يسمح لمنسقي المقررات والمديرين ومنسقي البرامج
    if user.role not in [UserRole.ADMIN, UserRole.COURSE_COORDINATOR, UserRole.PROGRAM_COORDINATOR]:
        st.error(f"⛔ ليس لديك صلاحية للوصول إلى هذه الصفحة")
        return

    # الحصول على مقررات المستخدم
    all_courses = db.get_all_courses()

    if user.role == UserRole.COURSE_COORDINATOR:
        # منسق المقرر يرى مقرراته فقط
        user_data = db.load_users()
        assigned_courses = []
        for u in user_data:
            if u.get('user_id') == user.user_id:
                assigned_courses = u.get('assigned_courses', [])
                break
        courses = [c for c in all_courses
                  if c.get('course_id') in assigned_courses or c.get('coordinator_id') == user.user_id]
    elif user.role == UserRole.PROGRAM_COORDINATOR:
        # منسق البرنامج يرى مقررات برنامجه
        user_data = db.load_users()
        assigned_programs = []
        for u in user_data:
            if u.get('user_id') == user.user_id:
                assigned_programs = u.get('assigned_programs', [])
                break
        courses = [c for c in all_courses if c.get('program_id') in assigned_programs]
    else:
        # المدير يرى جميع المقررات
        courses = all_courses

    if not courses:
        st.warning("⚠️ لا توجد مقررات مسندة لك / No courses assigned to you")
        return

    # علامات التبويب
    tab1, tab2 = st.tabs([
        f"📋 عرض مخرجات التعلم / View CLOs",
        f"➕ إضافة مخرج تعلم / Add CLO"
    ])

    with tab1:
        show_clos_list(db, user, courses, lang, is_rtl)

    with tab2:
        show_add_clo_form(db, user, courses, lang, is_rtl)


def show_clos_list(db: Database, user, courses, lang: str, is_rtl: bool):
    """عرض قائمة مخرجات التعلم"""

    st.subheader("📋 قائمة مخرجات التعلم / CLOs List")

    # اختيار المقرر
    course_options = {
        f"{c.get('course_code', '')} - {c.get('course_title_ar' if lang == 'ar' else 'course_title_en', '')}": c.get('course_id')
        for c in courses
    }

    if not course_options:
        st.info("ℹ️ لا توجد مقررات متاحة")
        return

    selected_course_name = st.selectbox(
        "🎯 اختر المقرر / Select Course:",
        options=list(course_options.keys()),
        key='view_course_selection'
    )

    selected_course_id = course_options[selected_course_name]
    selected_course = next((c for c in courses if c.get('course_id') == selected_course_id), None)
    program_id = selected_course.get('program_id') if selected_course else None

    # تحميل CLOs للمقرر المحدد
    clos_data = load_clos_data()
    course_clos = [clo for clo in clos_data.get('clos', []) if clo.get('course_id') == selected_course_id]

    if not course_clos:
        st.info("ℹ️ لا توجد مخرجات تعلم لهذا المقرر بعد / No CLOs defined for this course yet")
        return

    # عرض رسائل النجاح
    if st.session_state.get('clo_update_success'):
        st.success("✅ تم تحديث المخرج بنجاح / CLO updated successfully")
        st.session_state['clo_update_success'] = False

    if st.session_state.get('clo_delete_success'):
        st.success("✅ تم حذف المخرج بنجاح / CLO deleted successfully")
        st.session_state['clo_delete_success'] = False

    # التحقق من وجود CLO في وضع التعديل
    editing_clo_id = st.session_state.get('editing_clo_id')

    # عرض نموذج التعديل إذا كان موجود
    if editing_clo_id:
        editing_clo = next((clo for clo in course_clos if clo.get('clo_id') == editing_clo_id), None)
        if editing_clo:
            show_edit_clo_form(db, editing_clo, program_id, lang)
            return

    # عرض CLOs في جدول
    st.markdown(f"**إجمالي مخرجات التعلم / Total CLOs:** {len(course_clos)}")
    st.markdown("")

    for i, clo in enumerate(course_clos, 1):
        with st.container():
            # عنوان CLO
            st.markdown(f"### CLO {i}: {clo.get('clo_code', '')}")
            st.markdown(f"**المجال / Domain:** {clo.get('domain', 'غير محدد')}")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**الوصف بالعربية:**")
                st.markdown(f"> {clo.get('description_ar', 'بدون وصف')}")

            with col2:
                st.markdown(f"**Description (English):**")
                st.markdown(f"> {clo.get('description_en', 'No description')}")

            # معلومات إضافية
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**مخرجات البرنامج المرتبطة / Related PLOs:** {', '.join(clo.get('related_plos', [])) if clo.get('related_plos') else 'لا يوجد'}")
            with col2:
                st.markdown(f"**طرق القياس / Assessment Methods:** {', '.join(clo.get('assessment_methods', [])) if clo.get('assessment_methods') else 'لا يوجد'}")

            # أزرار التحكم
            col1, col2, col3 = st.columns([1, 1, 8])
            with col1:
                if st.button("✏️ تعديل", key=f"edit_{clo.get('clo_id')}"):
                    st.session_state['editing_clo_id'] = clo.get('clo_id')
                    st.rerun()

            with col2:
                if st.button("🗑️ حذف", key=f"delete_{clo.get('clo_id')}"):
                    st.session_state['deleting_clo_id'] = clo.get('clo_id')
                    st.rerun()

            # تأكيد الحذف
            if st.session_state.get('deleting_clo_id') == clo.get('clo_id'):
                st.warning(f"⚠️ هل أنت متأكد من حذف المخرج **{clo.get('clo_code')}**؟")
                col_yes, col_no, col_space = st.columns([1, 1, 8])
                with col_yes:
                    if st.button("✅ نعم", key=f"confirm_delete_{clo.get('clo_id')}"):
                        if delete_clo(clo.get('clo_id')):
                            st.session_state['clo_delete_success'] = True
                            st.session_state['deleting_clo_id'] = None
                            st.rerun()
                with col_no:
                    if st.button("❌ لا", key=f"cancel_delete_{clo.get('clo_id')}"):
                        st.session_state['deleting_clo_id'] = None
                        st.rerun()

            st.markdown("---")


def show_edit_clo_form(db: Database, clo: dict, program_id: str, lang: str):
    """نموذج تعديل مخرج تعلم"""

    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 20px; border-radius: 10px; margin-bottom: 20px;
                border: 3px solid #ff4757;">
        <h3 style="color: white; margin: 0; text-align: center;">
            ✏️ تعديل مخرج التعلم / Edit CLO
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # زر إلغاء التعديل
    if st.button("❌ إلغاء التعديل / Cancel Edit", type='secondary'):
        st.session_state['editing_clo_id'] = None
        st.rerun()

    with st.form("edit_clo_form"):
        # رمز المخرج
        clo_code = st.text_input(
            "رمز المخرج / CLO Code: *",
            value=clo.get('clo_code', ''),
            placeholder="مثال: K1, S1, V1"
        )

        col1, col2 = st.columns(2)

        with col1:
            description_ar = st.text_area(
                "وصف المخرج بالعربية / Description (Arabic): *",
                value=clo.get('description_ar', ''),
                height=100
            )

        with col2:
            description_en = st.text_area(
                "وصف المخرج بالإنجليزية / Description (English): *",
                value=clo.get('description_en', ''),
                height=100
            )

        # مجال المخرج
        domain_options = [
            "المعارف / Knowledge",
            "المهارات / Skills",
            "القيم / Values"
        ]
        current_domain = clo.get('domain', domain_options[0])
        domain_index = domain_options.index(current_domain) if current_domain in domain_options else 0

        clo_domain = st.selectbox(
            "مجال المخرج / CLO Domain: *",
            options=domain_options,
            index=domain_index
        )

        # مخرجات البرنامج المرتبطة
        plos_options = get_plos_for_program(db, program_id) if program_id else []
        current_plos = clo.get('related_plos', [])

        if plos_options:
            related_plos = st.multiselect(
                "مخرجات البرنامج المرتبطة / Related PLOs:",
                options=plos_options,
                default=[p for p in current_plos if p in plos_options]
            )
        else:
            related_plos = []

        # طرق القياس
        assessment_options = get_assessment_methods_for_program(db, program_id) if program_id else []
        current_methods = clo.get('assessment_methods', [])

        if assessment_options:
            assessment_methods = st.multiselect(
                "طرق القياس / Assessment Methods:",
                options=assessment_options,
                default=[m for m in current_methods if m in assessment_options]
            )
        else:
            assessment_methods = []

        is_active = st.checkbox("نشط / Active", value=clo.get('is_active', True))

        submitted = st.form_submit_button("💾 حفظ التعديلات / Save Changes", type="primary", use_container_width=True)

        if submitted:
            if not clo_code or not description_ar or not description_en:
                st.error("⚠️ يرجى ملء جميع الحقول المطلوبة / Please fill all required fields")
                return

            # تحديث بيانات CLO
            updated_clo = {
                **clo,
                "clo_code": clo_code,
                "description_ar": description_ar,
                "description_en": description_en,
                "domain": clo_domain,
                "related_plos": related_plos,
                "assessment_methods": assessment_methods,
                "is_active": is_active,
                "last_updated": datetime.now().isoformat()
            }

            if update_clo(updated_clo):
                st.session_state['clo_update_success'] = True
                st.session_state['editing_clo_id'] = None
                st.rerun()
            else:
                st.error("❌ حدث خطأ أثناء التحديث / Error updating CLO")


def show_add_clo_form(db: Database, user, courses, lang: str, is_rtl: bool):
    """نموذج إضافة مخرج تعلم جديد"""

    st.subheader("➕ إضافة مخرج تعلم جديد / Add New CLO")

    # عرض رسالة النجاح إذا كانت موجودة في session_state
    if st.session_state.get('clo_add_success'):
        clo_code = st.session_state.get('clo_add_code', '')
        st.success(f"✅ تم إضافة مخرج التعلم ({clo_code}) بنجاح / CLO ({clo_code}) added successfully")
        # مسح الرسالة من session_state
        st.session_state['clo_add_success'] = False
        st.session_state['clo_add_code'] = ''

    # اختيار المقرر - خارج النموذج لتجنب مشاكل إعادة التحميل
    course_list = [(f"{c.get('course_code', '')} - {c.get('course_title_ar' if lang == 'ar' else 'course_title_en', '')}", c) for c in courses]
    course_names = [name for name, _ in course_list]

    selected_course_name = st.selectbox(
        "🎯 اختر المقرر / Select Course: *",
        options=course_names,
        key='add_course_selection_main'
    )

    # الحصول على المقرر المحدد
    selected_course = next((c for name, c in course_list if name == selected_course_name), None)

    if not selected_course:
        st.error("❌ خطأ في تحميل المقرر")
        return

    selected_course_id = selected_course.get('course_id')
    program_id = selected_course.get('program_id')

    with st.form("add_clo_form"):
        # رمز المخرج
        clo_code = st.text_input(
            "رمز المخرج / CLO Code: *",
            placeholder="مثال: K1, S1, V1",
            help="رمز المخرج مثل K1, K2, S1, S2, V1..."
        )

        col1, col2 = st.columns(2)

        with col1:
            description_ar = st.text_area(
                "وصف المخرج بالعربية / Description (Arabic): *",
                height=100,
                placeholder="أدخل وصف مخرج التعلم بالعربية"
            )

        with col2:
            description_en = st.text_area(
                "وصف المخرج بالإنجليزية / Description (English): *",
                height=100,
                placeholder="Enter the CLO description in English"
            )

        # مجال المخرج (Domain)
        st.markdown("### 📚 مجال المخرج / CLO Domain")
        clo_domain = st.selectbox(
            "اختر مجال المخرج / Select CLO Domain: *",
            options=[
                "المعارف / Knowledge",
                "المهارات / Skills",
                "القيم / Values"
            ],
            help="حدد المجال الذي ينتمي إليه هذا المخرج"
        )

        # مخرجات البرنامج المرتبطة
        st.markdown("### 🎯 مخرجات البرنامج المرتبطة / Related PLOs")
        plos_options = get_plos_for_program(db, program_id) if program_id else []

        if plos_options:
            related_plos = st.multiselect(
                "اختر مخرجات البرنامج المرتبطة / Select Related PLOs:",
                options=plos_options,
                help="اختر رموز مخرجات البرنامج المرتبطة بهذا المخرج"
            )
        else:
            st.warning("⚠️ لم يتم تعريف مخرجات للبرنامج بعد. يرجى إضافة مخرجات البرنامج أولاً.")
            related_plos = []

        # طرق القياس
        st.markdown("### 📊 طرق القياس / Assessment Methods")
        assessment_methods_options = get_assessment_methods_for_program(db, program_id) if program_id else []

        if assessment_methods_options:
            assessment_methods = st.multiselect(
                "اختر طرق القياس / Select Assessment Methods:",
                options=assessment_methods_options,
                help="اختر طرق القياس من القائمة المُعرّفة للبرنامج"
            )
        else:
            st.warning("⚠️ لم يتم تعريف طرق قياس للبرنامج بعد. يرجى إضافة طرق القياس في إعدادات البرنامج.")
            assessment_methods = []

        is_active = st.checkbox("نشط / Active", value=True)

        submitted = st.form_submit_button("➕ إضافة المخرج / Add CLO", type="primary", use_container_width=True)

        if submitted:
            # التحقق من البيانات
            if not clo_code or not description_ar or not description_en:
                st.error("⚠️ يرجى ملء جميع الحقول المطلوبة / Please fill all required fields")
                return

            # إنشاء CLO جديد
            import secrets
            clo_id = f"clo_{secrets.token_hex(6)}"

            new_clo = {
                "clo_id": clo_id,
                "course_id": selected_course_id,
                "clo_code": clo_code,
                "description_ar": description_ar,
                "description_en": description_en,
                "domain": clo_domain,
                "related_plos": related_plos,
                "assessment_methods": assessment_methods,
                "is_active": is_active,
                "created_by": user.user_id,
                "created_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }

            # حفظ CLO
            if save_clo(new_clo):
                # حفظ رسالة النجاح في session_state لعرضها بعد إعادة التحميل
                st.session_state['clo_add_success'] = True
                st.session_state['clo_add_code'] = clo_code
                st.rerun()
            else:
                st.error("❌ حدث خطأ أثناء الحفظ / Error saving CLO")


def load_clos_data():
    """تحميل بيانات CLOs من الملف"""
    clos_file = Path(__file__).parent.parent / 'data' / 'clos.json'

    if clos_file.exists():
        try:
            with open(clos_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"clos": [], "last_updated": datetime.now().isoformat()}
    else:
        return {"clos": [], "last_updated": datetime.now().isoformat()}


def save_clo(clo_data):
    """حفظ CLO جديد"""
    clos_file = Path(__file__).parent.parent / 'data' / 'clos.json'

    # تحميل البيانات الحالية
    data = load_clos_data()

    # إضافة CLO الجديد
    data['clos'].append(clo_data)
    data['last_updated'] = datetime.now().isoformat()

    # حفظ البيانات
    try:
        clos_file.parent.mkdir(parents=True, exist_ok=True)
        with open(clos_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False


def delete_clo(clo_id):
    """حذف CLO"""
    clos_file = Path(__file__).parent.parent / 'data' / 'clos.json'

    data = load_clos_data()
    data['clos'] = [clo for clo in data['clos'] if clo.get('clo_id') != clo_id]
    data['last_updated'] = datetime.now().isoformat()

    try:
        with open(clos_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def update_clo(updated_clo):
    """تحديث CLO موجود"""
    clos_file = Path(__file__).parent.parent / 'data' / 'clos.json'

    data = load_clos_data()

    # البحث عن CLO وتحديثه
    for i, clo in enumerate(data['clos']):
        if clo.get('clo_id') == updated_clo.get('clo_id'):
            data['clos'][i] = updated_clo
            break

    data['last_updated'] = datetime.now().isoformat()

    try:
        with open(clos_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def get_plos_for_program(db: Database, program_id):
    """الحصول على PLOs للبرنامج من قاعدة البيانات"""
    if not program_id:
        return []

    # إعادة تحميل البرامج من الملف مباشرة لتجنب التخزين المؤقت
    programs = db.load_programs()
    program = next((p for p in programs if p.get('program_id') == program_id), None)

    if program and program.get('plos'):
        # إرجاع رموز PLOs فقط
        return [plo.get('plo_code', '') for plo in program.get('plos', [])]

    return []


def get_assessment_methods_for_program(db: Database, program_id):
    """الحصول على طرق القياس المُعرّفة للبرنامج"""
    if not program_id:
        return []

    # إعادة تحميل البرامج من الملف مباشرة لتجنب التخزين المؤقت
    programs = db.load_programs()
    program = next((p for p in programs if p.get('program_id') == program_id), None)

    if program and program.get('assessment_methods'):
        return program.get('assessment_methods', [])

    return []

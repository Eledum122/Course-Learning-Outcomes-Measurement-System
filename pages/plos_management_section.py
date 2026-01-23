"""
قسم إدارة مخرجات البرنامج (PLOs) وطرق القياس
PLOs and Assessment Methods Management Section
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from models.database import Database, UserRole


def show_plos_management(db: Database, user, programs, lang: str, is_rtl: bool):
    """عرض صفحة إدارة مخرجات البرنامج وطرق القياس"""

    st.subheader("🎯 إدارة مخرجات البرنامج وطرق القياس")
    st.markdown("---")

    if not programs:
        st.warning("⚠️ لا توجد برامج متاحة")
        return

    # اختيار البرنامج
    program_options = {
        f"{p.get('program_code', '')} - {p.get('program_name_ar' if lang == 'ar' else 'program_name_en', '')}": p.get('program_id')
        for p in programs
    }

    selected_program_name = st.selectbox(
        "🏛️ اختر البرنامج / Select Program:",
        options=list(program_options.keys()),
        key='plo_program_selection'
    )

    selected_program_id = program_options[selected_program_name]
    selected_program = next((p for p in programs if p.get('program_id') == selected_program_id), None)

    if not selected_program:
        st.error("❌ خطأ في تحميل البرنامج")
        return

    # عرض قسمين: PLOs و طرق القياس
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📚 مخرجات البرنامج (PLOs)")
        manage_plos(db, selected_program, lang)

    with col2:
        st.markdown("### 📊 طرق القياس")
        manage_assessment_methods(db, selected_program, lang)


def manage_plos(db: Database, program, lang: str):
    """إدارة مخرجات البرنامج"""

    program_id = program.get('program_id')
    current_plos = program.get('plos', [])

    # عرض PLOs الحالية
    if current_plos:
        st.markdown(f"**عدد المخرجات الحالية:** {len(current_plos)}")
        st.markdown("")

        for i, plo in enumerate(current_plos):
            plo_code = plo.get('plo_code', f'PLO_{i}')
            desc_ar = plo.get('description_ar', 'بدون وصف')
            desc_en = plo.get('description_en', 'No description')
            domain = plo.get('domain', 'غير محدد')

            # عرض في بطاقة
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"### {plo_code}")
                    st.markdown(f"**المجال:** {domain}")
                    st.markdown(f"**الوصف (عربي):** {desc_ar}")
                    st.markdown(f"**الوصف (إنجليزي):** {desc_en}")
                with col2:
                    st.write("")
                    st.write("")
                    if st.button(f"🗑️ حذف", key=f"delete_plo_{program_id}_{i}"):
                        if delete_plo_from_program(db, program_id, plo_code):
                            st.success("✅ تم الحذف بنجاح")
                            st.rerun()
                st.markdown("---")
    else:
        st.info("ℹ️ لم يتم إضافة مخرجات للبرنامج بعد")

    st.markdown("---")

    # نموذج إضافة PLO جديد
    with st.form(key=f'add_plo_form_{program_id}'):
        st.markdown("#### ➕ إضافة مخرج جديد")

        plo_code = st.text_input(
            "رمز المخرج / PLO Code: *",
            placeholder="مثال: K1, K2, S1, S2",
            help="مثل K1, S1, V1..."
        )

        plo_domain = st.selectbox(
            "المجال / Domain: *",
            options=["المعارف / Knowledge", "المهارات / Skills", "القيم / Values"]
        )

        plo_desc_ar = st.text_area(
            "الوصف بالعربية / Description (Arabic): *",
            height=80,
            placeholder="وصف مخرج البرنامج بالعربية"
        )

        plo_desc_en = st.text_area(
            "الوصف بالإنجليزية / Description (English): *",
            height=80,
            placeholder="PLO description in English"
        )

        submitted = st.form_submit_button("➕ إضافة المخرج", type="primary", use_container_width=True)

        if submitted:
            if not plo_code or not plo_desc_ar or not plo_desc_en:
                st.error("⚠️ يرجى ملء جميع الحقول المطلوبة")
            else:
                new_plo = {
                    "plo_code": plo_code,
                    "domain": plo_domain,
                    "description_ar": plo_desc_ar,
                    "description_en": plo_desc_en,
                    "created_date": datetime.now().isoformat()
                }

                if add_plo_to_program(db, program_id, new_plo):
                    st.success("✅ تم إضافة المخرج بنجاح")
                    st.rerun()
                else:
                    st.error("❌ فشل في إضافة المخرج")


def manage_assessment_methods(db: Database, program, lang: str):
    """إدارة طرق القياس"""

    program_id = program.get('program_id')
    current_methods = program.get('assessment_methods', [])

    # عرض طرق القياس الحالية
    if current_methods:
        st.markdown(f"**عدد طرق القياس الحالية:** {len(current_methods)}")

        for i, method in enumerate(current_methods):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"✓ {method}")
            with col2:
                if st.button("🗑️", key=f"delete_method_{i}"):
                    if delete_assessment_method_from_program(db, program_id, method):
                        st.success("✅ تم الحذف")
                        st.rerun()
    else:
        st.info("ℹ️ لم يتم إضافة طرق قياس بعد")

    st.markdown("---")

    # نموذج إضافة طريقة قياس جديدة
    with st.form(key=f'add_method_form_{program_id}'):
        st.markdown("#### ➕ إضافة طريقة قياس")

        method_name = st.text_input(
            "اسم طريقة القياس / Assessment Method Name: *",
            placeholder="مثال: الاختبار النصفي، المشروع، التقرير",
            help="أدخل اسم طريقة القياس"
        )

        submitted = st.form_submit_button("➕ إضافة", type="primary", use_container_width=True)

        if submitted:
            if not method_name:
                st.error("⚠️ يرجى إدخال اسم طريقة القياس")
            else:
                if add_assessment_method_to_program(db, program_id, method_name):
                    st.success("✅ تم إضافة طريقة القياس بنجاح")
                    st.rerun()
                else:
                    st.error("❌ فشل في إضافة طريقة القياس")


def add_plo_to_program(db: Database, program_id: str, plo_data: dict) -> bool:
    """إضافة PLO إلى البرنامج"""
    try:
        programs = db.load_programs()

        for program in programs:
            if program.get('program_id') == program_id:
                if 'plos' not in program:
                    program['plos'] = []

                # التحقق من عدم تكرار الرمز
                if any(p.get('plo_code') == plo_data.get('plo_code') for p in program['plos']):
                    return False

                program['plos'].append(plo_data)
                return db.save_programs(programs)

        return False
    except Exception as e:
        print(f"Error adding PLO: {e}")
        return False


def delete_plo_from_program(db: Database, program_id: str, plo_code: str) -> bool:
    """حذف PLO من البرنامج"""
    try:
        programs = db.load_programs()

        for program in programs:
            if program.get('program_id') == program_id:
                if 'plos' in program:
                    program['plos'] = [p for p in program['plos'] if p.get('plo_code') != plo_code]
                    return db.save_programs(programs)

        return False
    except Exception as e:
        print(f"Error deleting PLO: {e}")
        return False


def add_assessment_method_to_program(db: Database, program_id: str, method_name: str) -> bool:
    """إضافة طريقة قياس إلى البرنامج"""
    try:
        programs = db.load_programs()

        for program in programs:
            if program.get('program_id') == program_id:
                if 'assessment_methods' not in program:
                    program['assessment_methods'] = []

                # التحقق من عدم التكرار
                if method_name in program['assessment_methods']:
                    return False

                program['assessment_methods'].append(method_name)
                return db.save_programs(programs)

        return False
    except Exception as e:
        print(f"Error adding assessment method: {e}")
        return False


def delete_assessment_method_from_program(db: Database, program_id: str, method_name: str) -> bool:
    """حذف طريقة قياس من البرنامج"""
    try:
        programs = db.load_programs()

        for program in programs:
            if program.get('program_id') == program_id:
                if 'assessment_methods' in program:
                    program['assessment_methods'] = [m for m in program['assessment_methods'] if m != method_name]
                    return db.save_programs(programs)

        return False
    except Exception as e:
        print(f"Error deleting assessment method: {e}")
        return False

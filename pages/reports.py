"""
صفحة التقارير والإحصائيات
Reports and Statistics Page
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from models.database import Database, UserRole
from translations import t
import io
import json
from pathlib import Path


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


def show_reports(db: Database, user, lang: str):
    """عرض صفحة التقارير والإحصائيات"""

    is_rtl = lang == 'ar'

    st.title(f"📊 {t('reports', lang)}")

    # علامات التبويب للتقارير المختلفة
    tab1, tab2, tab3 = st.tabs([
        f"📈 {t('programs_statistics', lang) if lang == 'ar' else 'Programs Statistics'}",
        f"📚 {t('courses_statistics', lang) if lang == 'ar' else 'Courses Statistics'}",
        f"🔗 {t('clos_plos_mapping', lang) if lang == 'ar' else 'CLOs-PLOs Mapping'}"
    ])

    with tab1:
        show_programs_statistics(db, user, lang, is_rtl)

    with tab2:
        show_courses_statistics(db, user, lang, is_rtl)

    with tab3:
        show_clos_plos_mapping(db, user, lang, is_rtl)


def show_programs_statistics(db: Database, user, lang: str, is_rtl: bool):
    """عرض إحصائيات البرامج"""

    st.subheader(f"🏛️ {t('programs_statistics', lang) if lang == 'ar' else 'Programs Statistics'}")

    # تحميل البرامج
    all_programs = db.get_all_programs()

    # تصفية حسب الصلاحيات
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

    if not programs:
        st.info(f"ℹ️ {t('no_programs_found', lang)}")
        return

    # الإحصائيات الأساسية
    total_programs = len(programs)
    active_programs = len([p for p in programs if p.get('is_active', True)])
    inactive_programs = total_programs - active_programs

    # حساب PLOs
    total_plos = sum(len(p.get('plos', [])) for p in programs)
    programs_with_plos = len([p for p in programs if len(p.get('plos', [])) > 0])

    # حساب طرق القياس
    programs_with_assessment = len([p for p in programs if len(p.get('assessment_methods', [])) > 0])

    # عرض البطاقات الإحصائية
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px; border-radius: 10px; color: white; text-align: center;">
            <h2 style="color: white; margin: 0;">📊 {total_programs}</h2>
            <p style="color: white; margin: 5px 0;">إجمالي البرامج<br>Total Programs</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 20px; border-radius: 10px; color: white; text-align: center;">
            <h2 style="color: white; margin: 0;">✅ {active_programs}</h2>
            <p style="color: white; margin: 5px 0;">البرامج النشطة<br>Active Programs</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    padding: 20px; border-radius: 10px; color: white; text-align: center;">
            <h2 style="color: white; margin: 0;">🎯 {total_plos}</h2>
            <p style="color: white; margin: 5px 0;">إجمالي PLOs<br>Total PLOs</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                    padding: 20px; border-radius: 10px; color: white; text-align: center;">
            <h2 style="color: white; margin: 0;">📋 {programs_with_plos}</h2>
            <p style="color: white; margin: 5px 0;">برامج بها PLOs<br>Programs with PLOs</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # جدول تفصيلي للبرامج
    st.subheader(f"📋 {t('programs_details', lang) if lang == 'ar' else 'Programs Details'}")

    programs_data = []
    for program in programs:
        programs_data.append({
            'رمز البرنامج / Code': program.get('program_code', ''),
            'اسم البرنامج / Program Name': program.get('program_name_ar' if lang == 'ar' else 'program_name_en', ''),
            'عدد PLOs / PLOs Count': len(program.get('plos', [])),
            'طرق القياس / Assessment Methods': len(program.get('assessment_methods', [])),
            'الحالة / Status': '✅ نشط / Active' if program.get('is_active', True) else '❌ غير نشط / Inactive'
        })

    df_programs = pd.DataFrame(programs_data)
    st.dataframe(df_programs, use_container_width=True, hide_index=True)

    # زر تصدير Excel
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        excel_data = export_to_excel(df_programs, "تقرير إحصائيات البرامج")
        st.download_button(
            label="📥 تصدير إلى Excel / Export to Excel",
            data=excel_data,
            file_name=f"programs_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


def show_courses_statistics(db: Database, user, lang: str, is_rtl: bool):
    """عرض إحصائيات المقررات"""

    st.subheader(f"📚 {t('courses_statistics', lang) if lang == 'ar' else 'Courses Statistics'}")

    # تحميل المقررات
    all_courses = db.get_all_courses()
    all_programs = db.get_all_programs()

    # تصفية حسب الصلاحيات
    if user.role == UserRole.PROGRAM_COORDINATOR:
        user_data = db.load_users()
        assigned_programs = []
        for u in user_data:
            if u.get('user_id') == user.user_id:
                assigned_programs = u.get('assigned_programs', [])
                break
        courses = [c for c in all_courses if c.get('program_id') in assigned_programs]
    elif user.role == UserRole.COURSE_COORDINATOR:
        user_data = db.load_users()
        assigned_courses = []
        for u in user_data:
            if u.get('user_id') == user.user_id:
                assigned_courses = u.get('assigned_courses', [])
                break
        courses = [c for c in all_courses
                  if c.get('course_id') in assigned_courses or c.get('coordinator_id') == user.user_id]
    else:
        courses = all_courses

    if not courses:
        st.info(f"ℹ️ {t('no_courses_found', lang)}")
        return

    # تحميل CLOs
    clos_data = load_clos_data()
    all_clos = clos_data.get('clos', [])

    # الإحصائيات الأساسية
    total_courses = len(courses)
    active_courses = len([c for c in courses if c.get('is_active', True)])

    # حساب CLOs
    course_ids = [c.get('course_id') for c in courses]
    total_clos = len([clo for clo in all_clos if clo.get('course_id') in course_ids])
    courses_with_clos = len(set([clo.get('course_id') for clo in all_clos if clo.get('course_id') in course_ids]))

    # حساب الساعات المعتمدة
    total_credit_hours = sum(c.get('credit_hours', 0) for c in courses)

    # عرض البطاقات الإحصائية
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                    padding: 20px; border-radius: 10px; color: white; text-align: center;">
            <h2 style="color: white; margin: 0;">📚 {total_courses}</h2>
            <p style="color: white; margin: 5px 0;">إجمالي المقررات<br>Total Courses</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
                    padding: 20px; border-radius: 10px; color: white; text-align: center;">
            <h2 style="color: white; margin: 0;">✅ {active_courses}</h2>
            <p style="color: white; margin: 5px 0;">المقررات النشطة<br>Active Courses</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                    padding: 20px; border-radius: 10px; color: #333; text-align: center;">
            <h2 style="color: #333; margin: 0;">🎯 {total_clos}</h2>
            <p style="color: #333; margin: 5px 0;">إجمالي CLOs<br>Total CLOs</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%);
                    padding: 20px; border-radius: 10px; color: white; text-align: center;">
            <h2 style="color: white; margin: 0;">⏰ {total_credit_hours}</h2>
            <p style="color: white; margin: 5px 0;">إجمالي الساعات<br>Total Credit Hours</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # جدول تفصيلي للمقررات
    st.subheader(f"📋 {t('courses_details', lang) if lang == 'ar' else 'Courses Details'}")

    # إنشاء قاموس للبرامج
    programs_dict = {p.get('program_id'): p.get('program_name_ar' if lang == 'ar' else 'program_name_en', '') for p in all_programs}

    courses_data = []
    for course in courses:
        course_id = course.get('course_id')
        clos_count = len([clo for clo in all_clos if clo.get('course_id') == course_id])
        program_name = programs_dict.get(course.get('program_id', ''), 'N/A')

        courses_data.append({
            'رمز المقرر / Code': course.get('course_code', ''),
            'اسم المقرر / Course Name': course.get('course_title_ar' if lang == 'ar' else 'course_title_en', ''),
            'البرنامج / Program': program_name,
            'الساعات / Credit Hours': course.get('credit_hours', 0),
            'عدد CLOs / CLOs Count': clos_count,
            'الحالة / Status': '✅ نشط / Active' if course.get('is_active', True) else '❌ غير نشط / Inactive'
        })

    df_courses = pd.DataFrame(courses_data)
    st.dataframe(df_courses, use_container_width=True, hide_index=True)

    # زر تصدير Excel
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        excel_data = export_to_excel(df_courses, "تقرير إحصائيات المقررات")
        st.download_button(
            label="📥 تصدير إلى Excel / Export to Excel",
            data=excel_data,
            file_name=f"courses_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


def show_clos_plos_mapping(db: Database, user, lang: str, is_rtl: bool):
    """عرض تقرير ربط CLOs بـ PLOs"""

    st.subheader(f"🔗 {t('clos_plos_mapping', lang) if lang == 'ar' else 'CLOs-PLOs Mapping Report'}")

    # تحميل البيانات
    all_programs = db.get_all_programs()
    all_courses = db.get_all_courses()
    clos_data = load_clos_data()
    all_clos = clos_data.get('clos', [])

    # تصفية حسب الصلاحيات
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

    if not programs:
        st.info(f"ℹ️ {t('no_programs_found', lang)}")
        return

    # اختيار برنامج
    program_options = {
        f"{p.get('program_code', '')} - {p.get('program_name_ar' if lang == 'ar' else 'program_name_en', '')}": p.get('program_id')
        for p in programs
    }

    selected_program_name = st.selectbox(
        "🏛️ اختر البرنامج / Select Program:",
        options=list(program_options.keys()),
        key='report_program_select'
    )

    selected_program_id = program_options[selected_program_name]
    selected_program = next((p for p in programs if p.get('program_id') == selected_program_id), None)

    if not selected_program:
        return

    # الحصول على PLOs للبرنامج
    plos = selected_program.get('plos', [])

    if not plos:
        st.warning(f"⚠️ البرنامج المحدد لا يحتوي على PLOs / The selected program has no PLOs")
        return

    # الحصول على مقررات البرنامج
    program_courses = [c for c in all_courses if c.get('program_id') == selected_program_id]

    if not program_courses:
        st.warning(f"⚠️ البرنامج المحدد لا يحتوي على مقررات / The selected program has no courses")
        return

    # إنشاء جدول الربط
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"### 📊 جدول ربط CLOs بـ PLOs")
    st.markdown(f"**البرنامج:** {selected_program.get('program_name_ar' if lang == 'ar' else 'program_name_en', '')}")

    # إنشاء DataFrame للربط
    mapping_data = []

    for course in program_courses:
        course_id = course.get('course_id')
        course_clos = [clo for clo in all_clos if clo.get('course_id') == course_id]

        for clo in course_clos:
            related_plos = clo.get('related_plos', [])
            plos_str = ', '.join(related_plos) if related_plos else 'N/A'

            mapping_data.append({
                'رمز المقرر / Course Code': course.get('course_code', ''),
                'اسم المقرر / Course Name': course.get('course_title_ar' if lang == 'ar' else 'course_title_en', ''),
                'رمز CLO / CLO Code': clo.get('clo_code', ''),
                'وصف CLO / CLO Description': clo.get('description_ar' if lang == 'ar' else 'description_en', '')[:50] + '...',
                'PLOs المرتبطة / Related PLOs': plos_str
            })

    if mapping_data:
        df_mapping = pd.DataFrame(mapping_data)
        st.dataframe(df_mapping, use_container_width=True, hide_index=True)

        # إحصائيات الربط
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        with col1:
            total_clos = len(mapping_data)
            st.metric("إجمالي CLOs / Total CLOs", total_clos)

        with col2:
            clos_with_plos = len([m for m in mapping_data if m['PLOs المرتبطة / Related PLOs'] != 'N/A'])
            st.metric("CLOs مربوطة بـ PLOs / CLOs Mapped", clos_with_plos)

        with col3:
            mapping_percentage = round((clos_with_plos / total_clos * 100) if total_clos > 0 else 0, 1)
            st.metric("نسبة الربط / Mapping %", f"{mapping_percentage}%")

        # زر تصدير Excel
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            excel_data = export_to_excel(df_mapping, f"تقرير ربط CLOs-PLOs - {selected_program.get('program_code', '')}")
            st.download_button(
                label="📥 تصدير إلى Excel / Export to Excel",
                data=excel_data,
                file_name=f"clos_plos_mapping_{selected_program.get('program_code', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    else:
        st.info(f"ℹ️ لا توجد CLOs مسجلة لمقررات هذا البرنامج / No CLOs found for this program's courses")


def export_to_excel(df: pd.DataFrame, sheet_name: str) -> bytes:
    """تصدير DataFrame إلى ملف Excel"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name[:31], index=False)  # Excel sheet names max 31 chars

    output.seek(0)
    return output.getvalue()

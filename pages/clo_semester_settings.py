"""
إعدادات مخرجات التعلم حسب الفصل الدراسي
CLO Semester Settings - Adjust Target % and Criterion % per semester
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from models.database import Database, UserRole
from utils.permissions import get_permissions_helper


def load_clos_data():
    """تحميل بيانات مخرجات التعلم"""
    clos_file = Path(__file__).parent.parent / 'data' / 'clos.json'
    if clos_file.exists():
        try:
            with open(clos_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"clos": []}
    return {"clos": []}


def load_clo_semester_settings():
    """تحميل إعدادات CLOs حسب الفصل"""
    settings_file = Path(__file__).parent.parent / 'data' / 'clo_semester_settings.json'
    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"clo_semester_settings": []}
    return {"clo_semester_settings": []}


def save_clo_semester_settings(data):
    """حفظ إعدادات CLOs حسب الفصل"""
    settings_file = Path(__file__).parent.parent / 'data' / 'clo_semester_settings.json'
    try:
        data['last_updated'] = datetime.now().isoformat()
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def load_courses_data():
    """تحميل بيانات المقررات"""
    courses_file = Path(__file__).parent.parent / 'data' / 'courses.json'
    if courses_file.exists():
        try:
            with open(courses_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"courses": []}
    return {"courses": []}


def load_programs_data():
    """تحميل بيانات البرامج"""
    programs_file = Path(__file__).parent.parent / 'data' / 'programs.json'
    if programs_file.exists():
        try:
            with open(programs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"programs": []}
    return {"programs": []}


def get_courses_by_program(program_id, courses):
    """الحصول على مقررات البرنامج"""
    return [c for c in courses if c.get('program_id') == program_id]


def get_course_clos(course_id):
    """الحصول على مخرجات التعلم للمقرر"""
    clos_data = load_clos_data()
    return [clo for clo in clos_data.get('clos', []) if clo.get('course_id') == course_id and clo.get('is_active', True)]


def generate_semester_code(academic_year: str, semester_type: str) -> str:
    """توليد رمز الفصل الدراسي"""
    try:
        year = int(academic_year)
        last_two_digits = year % 100

        semester_map = {
            "First / الأول": "1",
            "Second / الثاني": "2",
            "Summer / صيفي": "5"
        }

        semester_num = semester_map.get(semester_type, "1")
        return f"{last_two_digits}{semester_num}"
    except:
        return ""


def get_clo_semester_setting(settings, course_id, semester_code, clo_id):
    """الحصول على إعداد CLO لفصل معين"""
    for setting in settings:
        if (setting.get('course_id') == course_id and
            setting.get('semester_code') == semester_code and
            setting.get('clo_id') == clo_id):
            return setting
    return None


def show_clo_semester_settings(db: Database, user, lang: str):
    """عرض صفحة إعدادات CLOs حسب الفصل الدراسي"""

    st.title("CLO Semester Settings / إعدادات المخرجات حسب الفصل")
    st.caption("Adjust Target % and Criterion % for each semester offering")

    # Initialize permissions helper
    perm = get_permissions_helper(db, user)

    # تحميل البيانات وتطبيق التصفية حسب الصلاحيات
    programs_data = load_programs_data()
    all_programs = programs_data.get('programs', [])
    programs = perm.filter_programs(all_programs)

    courses_data = load_courses_data()
    all_courses = courses_data.get('courses', [])
    courses = perm.filter_courses(all_courses)

    settings_data = load_clo_semester_settings()
    settings = settings_data.get('clo_semester_settings', [])

    # قائمة البرامج النشطة
    program_list = [(p.get('program_id'), f"{p.get('program_code', '')} - {p.get('program_name_en', '')}")
                    for p in programs if p.get('is_active', True)]

    # خيارات السنة والفصل
    academic_years = ["1446", "1447", "1448", "1449", "1450"]
    semester_options = ["First / الأول", "Second / الثاني", "Summer / صيفي"]

    # عرض رسالة النجاح
    if st.session_state.get('clo_settings_message'):
        msg_type, msg_text = st.session_state.clo_settings_message
        if msg_type == 'success':
            st.success(msg_text)
        elif msg_type == 'error':
            st.error(msg_text)
        st.session_state.clo_settings_message = None

    # ===============================
    # القسم 1: اختيار المقرر والفصل
    # ===============================
    st.markdown("### 1. Select Course and Semester / اختر المقرر والفصل")

    col1, col2 = st.columns(2)

    with col1:
        # اختيار البرنامج
        if program_list:
            program_options = ["-- Select Program --"] + [p[1] for p in program_list]
            selected_program_display = st.selectbox("Program / البرنامج", program_options, key="clo_set_program")

            selected_program_id = None
            if selected_program_display != "-- Select Program --":
                for p in program_list:
                    if p[1] == selected_program_display:
                        selected_program_id = p[0]
                        break
        else:
            st.warning("No active programs found")
            selected_program_id = None

        # اختيار المقرر
        selected_course = None
        if selected_program_id:
            program_courses = get_courses_by_program(selected_program_id, courses)
            if program_courses:
                course_options = ["-- Select Course --"] + [f"{c.get('course_code', '')} - {c.get('course_title_en', '')}" for c in program_courses]
                selected_course_display = st.selectbox("Course / المقرر", course_options, key="clo_set_course")

                if selected_course_display != "-- Select Course --":
                    for c in program_courses:
                        if f"{c.get('course_code', '')} - {c.get('course_title_en', '')}" == selected_course_display:
                            selected_course = c
                            break
            else:
                st.warning("No courses found for selected program")

    with col2:
        # اختيار السنة والفصل
        selected_year = st.selectbox("Academic Year / السنة", ["-- Select --"] + academic_years, key="clo_set_year")
        selected_semester = st.selectbox("Semester / الفصل", ["-- Select --"] + semester_options, key="clo_set_semester")

        # حساب رمز الفصل
        semester_code = ""
        if selected_year != "-- Select --" and selected_semester != "-- Select --":
            semester_code = generate_semester_code(selected_year, selected_semester)
            st.info(f"Semester Code: **{semester_code}**")

    # التحقق من اكتمال الاختيارات
    if not selected_course or not semester_code:
        st.info("Please select Program, Course, Year and Semester to continue")
        return

    st.markdown("---")

    # ===============================
    # القسم 2: عرض وتعديل إعدادات CLOs
    # ===============================
    course_clos = get_course_clos(selected_course.get('course_id'))

    if not course_clos:
        st.warning("No CLOs defined for this course. Please add CLOs first.")
        return

    st.markdown("### 2. CLO Settings for this Semester / إعدادات المخرجات لهذا الفصل")
    st.caption(f"Course: {selected_course.get('course_code')} | Semester: {selected_year} {selected_semester.split(' / ')[0]} ({semester_code})")

    # زر لنسخ القيم الأصلية
    col_copy1, col_copy2 = st.columns([1, 3])
    with col_copy1:
        if st.button("Copy Original Values / نسخ القيم الأصلية", use_container_width=True):
            st.session_state.copy_original_values = True
            st.rerun()

    # ترتيب CLOs حسب المجال
    knowledge_clos = [c for c in course_clos if 'Knowledge' in c.get('domain', '') or 'المعارف' in c.get('domain', '')]
    skills_clos = [c for c in course_clos if 'Skills' in c.get('domain', '') or 'المهارات' in c.get('domain', '')]
    values_clos = [c for c in course_clos if 'Values' in c.get('domain', '') or 'القيم' in c.get('domain', '')]

    all_sorted_clos = sorted(knowledge_clos, key=lambda x: x.get('clo_code', '')) + \
                      sorted(skills_clos, key=lambda x: x.get('clo_code', '')) + \
                      sorted(values_clos, key=lambda x: x.get('clo_code', ''))

    # رؤوس الأعمدة
    header_cols = st.columns([0.8, 1.2, 3, 1, 1.2, 1.2])
    with header_cols[0]:
        st.markdown("**Code**")
    with header_cols[1]:
        st.markdown("**Category**")
    with header_cols[2]:
        st.markdown("**Description**")
    with header_cols[3]:
        st.markdown("**Mark**")
    with header_cols[4]:
        st.markdown("**Criterion %**")
    with header_cols[5]:
        st.markdown("**Target %**")

    st.markdown("---")

    # تخزين القيم المدخلة
    clo_inputs = {}

    for clo in all_sorted_clos:
        clo_id = clo.get('clo_id')
        clo_code = clo.get('clo_code', '')
        course_id = selected_course.get('course_id')

        # تحديد المجال
        domain = clo.get('domain', '')
        if 'Knowledge' in domain or 'المعارف' in domain:
            category = "Knowledge"
            category_color = "#3498db"
        elif 'Skills' in domain or 'المهارات' in domain:
            category = "Skills"
            category_color = "#2ecc71"
        else:
            category = "Values"
            category_color = "#9b59b6"

        # الوصف المختصر
        desc = clo.get('description_en', '')
        if len(desc) > 45:
            desc = desc[:45] + '...'

        # القيم الأصلية من CLO
        original_mark = clo.get('mark', 0)
        original_criterion = clo.get('criterion_percentage', 70)
        original_target = clo.get('target_percentage', 70)

        # البحث عن إعدادات الفصل الحالي
        existing_setting = get_clo_semester_setting(settings, course_id, semester_code, clo_id)

        # تحديد القيم المستخدمة
        if st.session_state.get('copy_original_values'):
            current_criterion = original_criterion
            current_target = original_target
        elif existing_setting:
            current_criterion = existing_setting.get('criterion_percentage', original_criterion)
            current_target = existing_setting.get('target_percentage', original_target)
        else:
            current_criterion = original_criterion
            current_target = original_target

        cols = st.columns([0.8, 1.2, 3, 1, 1.2, 1.2])

        with cols[0]:
            st.markdown(f"**{clo_code}**")

        with cols[1]:
            st.markdown(f"<span style='color: {category_color}; font-weight: bold;'>{category}</span>", unsafe_allow_html=True)

        with cols[2]:
            st.caption(desc)

        with cols[3]:
            st.markdown(f"**{original_mark}**")

        with cols[4]:
            criterion = st.number_input(
                f"Criterion {clo_code}",
                min_value=50.0,
                max_value=100.0,
                value=float(current_criterion),
                step=1.0,
                key=f"sem_criterion_{clo_id}",
                label_visibility='collapsed'
            )

        with cols[5]:
            target = st.number_input(
                f"Target {clo_code}",
                min_value=float(criterion),
                max_value=100.0,
                value=float(max(current_target, criterion)),
                step=1.0,
                key=f"sem_target_{clo_id}",
                label_visibility='collapsed'
            )

        clo_inputs[clo_id] = {
            'criterion': criterion,
            'target': target,
            'clo_code': clo_code
        }

    # مسح علامة نسخ القيم
    if st.session_state.get('copy_original_values'):
        st.session_state.copy_original_values = False

    st.markdown("---")

    # ===============================
    # أزرار الحفظ
    # ===============================
    btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 1])

    with btn_col1:
        if st.button("Save Settings / حفظ الإعدادات", type="primary", use_container_width=True):
            course_id = selected_course.get('course_id')
            course_code = selected_course.get('course_code')

            # تحديث أو إضافة الإعدادات
            for clo_id, data in clo_inputs.items():
                existing = get_clo_semester_setting(settings, course_id, semester_code, clo_id)

                if existing:
                    # تحديث الإعداد الموجود
                    for i, s in enumerate(settings_data['clo_semester_settings']):
                        if (s.get('course_id') == course_id and
                            s.get('semester_code') == semester_code and
                            s.get('clo_id') == clo_id):
                            settings_data['clo_semester_settings'][i]['criterion_percentage'] = data['criterion']
                            settings_data['clo_semester_settings'][i]['target_percentage'] = data['target']
                            settings_data['clo_semester_settings'][i]['updated_at'] = datetime.now().isoformat()
                            break
                else:
                    # إضافة إعداد جديد
                    new_setting = {
                        "setting_id": f"clsset_{course_id}_{semester_code}_{clo_id}",
                        "course_id": course_id,
                        "course_code": course_code,
                        "semester_code": semester_code,
                        "academic_year": selected_year,
                        "semester": selected_semester,
                        "clo_id": clo_id,
                        "clo_code": data['clo_code'],
                        "criterion_percentage": data['criterion'],
                        "target_percentage": data['target'],
                        "created_at": datetime.now().isoformat()
                    }
                    settings_data['clo_semester_settings'].append(new_setting)

            if save_clo_semester_settings(settings_data):
                st.session_state.clo_settings_message = ('success', f"Settings saved successfully for {course_code} - {semester_code}")
                st.rerun()
            else:
                st.session_state.clo_settings_message = ('error', "Error saving settings!")
                st.rerun()

    with btn_col2:
        if st.button("Reset / إعادة تعيين", use_container_width=True):
            st.rerun()

    # ===============================
    # عرض الإعدادات المحفوظة للمقرر
    # ===============================
    st.markdown("---")
    st.markdown("### 3. Saved Settings History / سجل الإعدادات المحفوظة")

    course_settings = [s for s in settings if s.get('course_id') == selected_course.get('course_id')]

    if course_settings:
        # تجميع حسب الفصل
        semesters = {}
        for s in course_settings:
            sem_code = s.get('semester_code', '')
            if sem_code not in semesters:
                semesters[sem_code] = {
                    'year': s.get('academic_year', ''),
                    'semester': s.get('semester', ''),
                    'count': 0
                }
            semesters[sem_code]['count'] += 1

        # عرض الفصول المحفوظة
        st.markdown("**Semesters with saved settings:**")
        for sem_code, info in sorted(semesters.items(), reverse=True):
            sem_display = info['semester'].split(' / ')[0] if ' / ' in info['semester'] else info['semester']
            is_current = sem_code == semester_code
            marker = " (Current)" if is_current else ""
            st.caption(f"- {info['year']} {sem_display} ({sem_code}): {info['count']} CLOs configured{marker}")
    else:
        st.info("No saved settings for this course yet")

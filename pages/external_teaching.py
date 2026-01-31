"""
صفحة إدارة التدريس الخارجي
External Teaching Management Page
المقررات التي يتم تدريسها لأقسام في كليات أخرى
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from models.database import Database, UserRole
from translations import t


def load_external_assignments():
    """تحميل تعيينات التدريس الخارجي"""
    try:
        with open('data/external_teaching.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('external_assignments', [])
    except:
        return []


def save_external_assignments(assignments):
    """حفظ تعيينات التدريس الخارجي"""
    with open('data/external_teaching.json', 'w', encoding='utf-8') as f:
        json.dump({
            "external_assignments": assignments,
            "last_updated": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)


def load_courses():
    """تحميل المقررات"""
    try:
        with open('data/courses.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('courses', [])
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


def show_external_teaching(db: Database, user, lang: str):
    """عرض صفحة إدارة التدريس الخارجي"""

    is_rtl = lang == 'ar'

    st.title("🏫 التدريس الخارجي / External Teaching")
    st.markdown("إدارة المقررات التي يتم تدريسها لأقسام في كليات أخرى / Manage courses taught to departments in other colleges")

    # التحقق من الصلاحيات
    if user.role not in [UserRole.ADMIN, UserRole.PROGRAM_COORDINATOR]:
        st.error(f"⛔ {t('no_permission', lang)}")
        return

    # تحميل البيانات
    courses = load_courses()
    programs = load_programs()
    assignments = load_external_assignments()

    # إنشاء قواميس للبحث السريع
    courses_dict = {c['course_id']: c for c in courses}
    programs_dict = {p['program_id']: p for p in programs}

    # علامات التبويب
    tab1, tab2, tab3 = st.tabs([
        "📋 قائمة التعيينات / Assignments List",
        "➕ إضافة تعيين جديد / Add New Assignment",
        "📊 إحصائيات / Statistics"
    ])

    # علامة التبويب الأولى: قائمة التعيينات
    with tab1:
        show_assignments_list(assignments, courses_dict, programs_dict, lang)

    # علامة التبويب الثانية: إضافة تعيين جديد
    with tab2:
        show_add_assignment_form(courses, programs, assignments, lang)

    # علامة التبويب الثالثة: إحصائيات
    with tab3:
        show_statistics(assignments, courses_dict, programs_dict, lang)


def show_assignments_list(assignments, courses_dict, programs_dict, lang):
    """عرض قائمة التعيينات"""

    st.subheader("📋 قائمة التدريس الخارجي / External Teaching List")

    if not assignments:
        st.info("ℹ️ لا توجد تعيينات تدريس خارجي حالياً / No external teaching assignments currently")
        return

    # تحويل إلى DataFrame
    data = []
    for a in assignments:
        course = courses_dict.get(a.get('course_id', ''), {})
        source_program = programs_dict.get(a.get('source_program_id', ''), {})

        data.append({
            'assignment_id': a.get('assignment_id', ''),
            'course_code': course.get('course_code', 'N/A'),
            'course_name': course.get('course_title_en', 'N/A'),
            'source_department': source_program.get('department_en', 'N/A'),
            'source_college': source_program.get('college_en', 'N/A'),
            'target_college': a.get('target_college_en', 'N/A'),
            'target_department': a.get('target_department_en', 'N/A'),
            'status': '✅ نشط' if a.get('is_active', True) else '❌ غير نشط'
        })

    df = pd.DataFrame(data)

    # عرض الجدول
    st.dataframe(
        df,
        column_config={
            'assignment_id': st.column_config.TextColumn('ID', width='small'),
            'course_code': st.column_config.TextColumn('رمز المقرر / Course Code', width='small'),
            'course_name': st.column_config.TextColumn('اسم المقرر / Course Name', width='medium'),
            'source_department': st.column_config.TextColumn('القسم المصدر / Source Dept.', width='medium'),
            'source_college': st.column_config.TextColumn('الكلية المصدر / Source College', width='medium'),
            'target_college': st.column_config.TextColumn('الكلية المستهدفة / Target College', width='medium'),
            'target_department': st.column_config.TextColumn('القسم المستهدف / Target Dept.', width='medium'),
            'status': st.column_config.TextColumn('الحالة / Status', width='small')
        },
        hide_index=True,
        use_container_width=True
    )

    st.info(f"📊 إجمالي التعيينات / Total Assignments: {len(assignments)}")

    # قسم التعديل والحذف
    st.markdown("---")
    st.subheader("✏️ تعديل أو حذف تعيين / Edit or Delete Assignment")

    assignment_options = {
        f"{courses_dict.get(a.get('course_id', ''), {}).get('course_code', 'N/A')} → {a.get('target_college_en', 'N/A')} / {a.get('target_department_en', 'N/A')}": a
        for a in assignments
    }

    if assignment_options:
        selected_key = st.selectbox(
            "اختر التعيين / Select Assignment",
            options=list(assignment_options.keys()),
            key="edit_assignment_select"
        )

        selected_assignment = assignment_options.get(selected_key)

        if selected_assignment:
            assignment_key = selected_assignment.get('assignment_id', 'unknown')

            col1, col2 = st.columns(2)

            with col1:
                # تعديل الحالة
                new_status = st.checkbox(
                    "نشط / Active",
                    value=selected_assignment.get('is_active', True),
                    key=f"edit_status_{assignment_key}"
                )

            with col2:
                # ملاحظات
                new_notes = st.text_area(
                    "ملاحظات / Notes",
                    value=selected_assignment.get('notes', ''),
                    key=f"edit_notes_{assignment_key}"
                )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("💾 حفظ التغييرات / Save Changes", type="primary", use_container_width=True, key=f"save_assignment_{assignment_key}"):
                    for a in assignments:
                        if a.get('assignment_id') == selected_assignment.get('assignment_id'):
                            a['is_active'] = new_status
                            a['notes'] = new_notes
                            a['last_updated'] = datetime.now().isoformat()
                            break

                    save_external_assignments(assignments)
                    st.success("✅ تم حفظ التغييرات / Changes saved successfully")
                    st.rerun()

            with col2:
                if st.button("🗑️ حذف التعيين / Delete Assignment", type="secondary", use_container_width=True, key=f"delete_assignment_{assignment_key}"):
                    st.session_state.confirm_delete_assignment = selected_assignment.get('assignment_id')

            # تأكيد الحذف
            if hasattr(st.session_state, 'confirm_delete_assignment') and st.session_state.confirm_delete_assignment == selected_assignment.get('assignment_id'):
                st.warning("⚠️ هل أنت متأكد من حذف هذا التعيين؟ / Are you sure you want to delete this assignment?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ نعم، احذف / Yes, Delete", type="primary", use_container_width=True, key=f"confirm_del_{assignment_key}"):
                        assignments = [a for a in assignments if a.get('assignment_id') != selected_assignment.get('assignment_id')]
                        save_external_assignments(assignments)
                        del st.session_state.confirm_delete_assignment
                        st.success("✅ تم حذف التعيين / Assignment deleted successfully")
                        st.rerun()
                with col2:
                    if st.button("❌ إلغاء / Cancel", use_container_width=True, key=f"cancel_del_{assignment_key}"):
                        del st.session_state.confirm_delete_assignment
                        st.rerun()


def show_add_assignment_form(courses, programs, assignments, lang):
    """عرض نموذج إضافة تعيين جديد"""

    st.subheader("➕ إضافة تعيين تدريس خارجي جديد / Add New External Teaching Assignment")

    if not courses:
        st.warning("⚠️ لا توجد مقررات مسجلة / No courses found")
        return

    if not programs:
        st.warning("⚠️ لا توجد برامج مسجلة / No programs found")
        return

    st.info("💡 التدريس الخارجي: تدريس مقرر من قسمك لطلاب قسم/كلية أخرى / External Teaching: Teaching a course from your department to students of another department/college")

    # اختيار المقرر
    course_options = {f"{c['course_code']} - {c['course_title_en']}": c for c in courses}
    selected_course_key = st.selectbox(
        "اختر المقرر / Select Course *",
        options=list(course_options.keys()),
        key="add_ext_course"
    )
    selected_course = course_options.get(selected_course_key)

    if selected_course:
        # عرض معلومات المقرر المصدر
        source_program = next((p for p in programs if p['program_id'] == selected_course.get('program_id')), None)
        course_key = selected_course.get('course_id', 'unknown')

        st.markdown("#### 📤 المصدر (القسم المالك للمقرر) / Source (Course Owner)")

        # عرض معلومات المصدر بشكل مباشر بدون text_input لتجنب مشاكل التحديث
        source_college = source_program.get('college_en', 'N/A') if source_program else 'N/A'
        source_dept = source_program.get('department_en', 'N/A') if source_program else 'N/A'

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**الكلية المصدر / Source College:**")
            st.info(f"🏛️ {source_college}")
        with col2:
            st.markdown(f"**القسم المصدر / Source Department:**")
            st.info(f"📚 {source_dept}")

    st.markdown("---")
    st.markdown("#### 📥 الجهة المستهدفة (المستفيدة) / Target (Beneficiary)")

    col1, col2 = st.columns(2)

    with col1:
        target_college_ar = st.text_input("الكلية المستهدفة (عربي) / Target College (Arabic) *", key="target_college_ar")
        target_college_en = st.text_input("الكلية المستهدفة (إنجليزي) / Target College (English) *", key="target_college_en")

    with col2:
        target_department_ar = st.text_input("القسم المستهدف (عربي) / Target Department (Arabic) *", key="target_dept_ar")
        target_department_en = st.text_input("القسم المستهدف (إنجليزي) / Target Department (English) *", key="target_dept_en")

    st.markdown("---")

    # ملاحظات (اختياري)
    notes = st.text_area("ملاحظات / Notes (Optional)", key="ext_notes")

    # زر الإضافة
    if st.button("➕ إضافة التعيين / Add Assignment", type="primary", use_container_width=True, key="add_ext_assignment_btn"):
        # التحقق من البيانات المطلوبة
        if not selected_course:
            st.error("⚠️ يرجى اختيار المقرر / Please select a course")
            return

        if not target_college_ar or not target_college_en:
            st.error("⚠️ يرجى إدخال الكلية المستهدفة / Please enter target college")
            return

        if not target_department_ar or not target_department_en:
            st.error("⚠️ يرجى إدخال القسم المستهدف / Please enter target department")
            return

        # التحقق من عدم التكرار
        for a in assignments:
            if (a.get('course_id') == selected_course['course_id'] and
                a.get('target_college_en') == target_college_en and
                a.get('target_department_en') == target_department_en):
                st.error("⚠️ هذا التعيين موجود مسبقاً / This assignment already exists")
                return

        # إنشاء التعيين الجديد
        source_program = next((p for p in programs if p['program_id'] == selected_course.get('program_id')), {})

        new_assignment = {
            "assignment_id": f"ext_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "course_id": selected_course['course_id'],
            "course_code": selected_course['course_code'],
            "source_program_id": selected_course.get('program_id', ''),
            "source_college_ar": source_program.get('college_ar', ''),
            "source_college_en": source_program.get('college_en', ''),
            "source_department_ar": source_program.get('department_ar', ''),
            "source_department_en": source_program.get('department_en', ''),
            "target_college_ar": target_college_ar,
            "target_college_en": target_college_en,
            "target_department_ar": target_department_ar,
            "target_department_en": target_department_en,
            "notes": notes,
            "is_active": True,
            "created_date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

        assignments.append(new_assignment)
        save_external_assignments(assignments)

        st.success("✅ تم إضافة تعيين التدريس الخارجي بنجاح / External teaching assignment added successfully")
        st.balloons()
        st.rerun()


def show_statistics(assignments, courses_dict, programs_dict, lang):
    """عرض إحصائيات التدريس الخارجي"""

    st.subheader("📊 إحصائيات التدريس الخارجي / External Teaching Statistics")

    if not assignments:
        st.info("ℹ️ لا توجد بيانات للإحصائيات / No data for statistics")
        return

    # إحصائيات عامة
    active_assignments = [a for a in assignments if a.get('is_active', True)]
    unique_courses = len(set(a.get('course_id') for a in active_assignments))
    unique_colleges = len(set(a.get('target_college_en') for a in active_assignments))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 15px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">إجمالي التعيينات</p>
            <p style="color: white; margin: 0; font-size: 32px; font-weight: bold; line-height: 1.2;">{len(assignments)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                    padding: 15px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">التعيينات النشطة</p>
            <p style="color: white; margin: 0; font-size: 32px; font-weight: bold; line-height: 1.2;">{len(active_assignments)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 15px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">عدد المقررات</p>
            <p style="color: white; margin: 0; font-size: 32px; font-weight: bold; line-height: 1.2;">{unique_courses}</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    padding: 15px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">عدد الكليات المستهدفة</p>
            <p style="color: white; margin: 0; font-size: 32px; font-weight: bold; line-height: 1.2;">{unique_colleges}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # التوزيع حسب الكليات المستهدفة
    st.markdown("### 🏛️ التوزيع حسب الكليات المستهدفة / Distribution by Target Colleges")

    target_colleges = {}
    for a in active_assignments:
        college = a.get('target_college_en', 'Unknown')
        if college not in target_colleges:
            target_colleges[college] = 0
        target_colleges[college] += 1

    if target_colleges:
        college_df = pd.DataFrame([
            {"الكلية / College": k, "عدد المقررات / Courses": v}
            for k, v in sorted(target_colleges.items(), key=lambda x: x[1], reverse=True)
        ])
        st.dataframe(college_df, hide_index=True, use_container_width=True)

    # التوزيع حسب المقررات
    st.markdown("### 📚 المقررات الأكثر تدريساً خارجياً / Most Externally Taught Courses")

    course_counts = {}
    for a in active_assignments:
        course_id = a.get('course_id', '')
        course = courses_dict.get(course_id, {})
        course_name = f"{course.get('course_code', 'N/A')} - {course.get('course_title_en', 'N/A')}"
        if course_name not in course_counts:
            course_counts[course_name] = 0
        course_counts[course_name] += 1

    if course_counts:
        course_df = pd.DataFrame([
            {"المقرر / Course": k, "عدد التعيينات / Assignments": v}
            for k, v in sorted(course_counts.items(), key=lambda x: x[1], reverse=True)
        ])
        st.dataframe(course_df, hide_index=True, use_container_width=True)

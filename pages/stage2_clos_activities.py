"""
المرحلة 2.4: توزيع المخرجات على الأنشطة
Stage 2.4: CLOs across Activities
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from models.database import Database, UserRole
from translations import t


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


def save_courses_data(data):
    """حفظ بيانات المقررات"""
    courses_file = Path(__file__).parent.parent / 'data' / 'courses.json'
    try:
        with open(courses_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


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


def load_topics_data():
    """تحميل بيانات موضوعات المقررات"""
    topics_file = Path(__file__).parent.parent / 'data' / 'course_topics.json'
    if topics_file.exists():
        try:
            with open(topics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"topics": []}
    return {"topics": []}


def get_course_clos(course_id):
    """الحصول على مخرجات التعلم للمقرر"""
    clos_data = load_clos_data()
    clos = [clo for clo in clos_data.get('clos', []) if clo.get('course_id') == course_id]
    return sorted(clos, key=lambda x: x.get('clo_code', ''))


def get_course_topics(course_id):
    """الحصول على موضوعات المقرر"""
    topics_data = load_topics_data()
    topics = [t for t in topics_data.get('topics', []) if t.get('course_id') == course_id]
    return sorted(topics, key=lambda x: int(x.get('topic_number', 0)))


def get_course_activities(course_id):
    """الحصول على أنشطة التقييم للمقرر"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            return course.get('assessment_activities', [])
    return []


def get_course_data(course_id):
    """الحصول على جميع بيانات المقرر"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            return course
    return {}


def get_clos_activities_distribution(course_id):
    """الحصول على توزيع المخرجات على الأنشطة"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            return course.get('clos_activities_distribution', {})
    return {}


def save_clos_activities_distribution(course_id, distribution):
    """حفظ توزيع المخرجات على الأنشطة"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            course['clos_activities_distribution'] = distribution
            course['last_updated'] = datetime.now().isoformat()
            break
    return save_courses_data(courses_data)


def get_clo_activity_relation(course_clos, course_activities):
    """
    تحديد العلاقة بين CLOs والأنشطة بناء على حقل assessment_methods في CLO
    هذا الربط تم في المرحلة الأولى (إدخال معلومات المقرر)
    """
    activity_names = [a.get('assessment_task') for a in course_activities]

    # إنشاء مصفوفة العلاقات من بيانات CLOs
    relations = {}

    for clo in course_clos:
        clo_code = clo.get('clo_code')
        # الحصول على طرق التقييم المرتبطة بهذا المخرج (من المرحلة الأولى)
        clo_assessment_methods = clo.get('assessment_methods', [])

        # إنشاء علاقة: True إذا كان النشاط موجود في assessment_methods
        relations[clo_code] = {}
        for act_name in activity_names:
            relations[clo_code][act_name] = act_name in clo_assessment_methods

    return relations


def show_stage2_clos_activities(db: Database, user, lang: str):
    """عرض صفحة توزيع المخرجات على الأنشطة"""

    st.title("📊 المرحلة 2.4: توزيع المخرجات على الأنشطة")
    st.markdown("### Stage 2.4: CLOs across Activities")

    # تحميل المقررات
    all_courses = db.get_all_courses()

    # تصفية المقررات حسب صلاحيات المستخدم
    if user.role == UserRole.COURSE_COORDINATOR:
        user_data = db.load_users()
        assigned_courses = []
        for u in user_data:
            if u.get('user_id') == user.user_id:
                assigned_courses = u.get('assigned_courses', [])
                break
        courses = [c for c in all_courses
                  if c.get('course_id') in assigned_courses or c.get('coordinator_id') == user.user_id]
    elif user.role == UserRole.PROGRAM_COORDINATOR:
        user_data = db.load_users()
        assigned_programs = []
        for u in user_data:
            if u.get('user_id') == user.user_id:
                assigned_programs = u.get('assigned_programs', [])
                break
        courses = [c for c in all_courses if c.get('program_id') in assigned_programs]
    else:
        courses = all_courses

    if not courses:
        st.warning("⚠️ لا توجد مقررات متاحة / No courses available")
        return

    # اختيار المقرر
    course_options = {
        f"{c.get('course_code', '')} - {c.get('course_title_ar', '')}": c.get('course_id')
        for c in courses
    }

    selected_course_name = st.selectbox(
        "🎯 اختر المقرر / Select Course:",
        options=list(course_options.keys()),
        key='clos_activities_course_select'
    )

    selected_course_id = course_options[selected_course_name]
    selected_course = next((c for c in courses if c.get('course_id') == selected_course_id), None)

    st.markdown("---")

    # الحصول على البيانات
    course_clos = get_course_clos(selected_course_id)
    course_topics = get_course_topics(selected_course_id)
    course_activities = get_course_activities(selected_course_id)
    course_data = get_course_data(selected_course_id)

    # التحقق من وجود البيانات
    missing_data = []
    if not course_clos:
        missing_data.append("مخرجات التعلم / CLOs")
    if not course_activities:
        missing_data.append("أنشطة التقييم / Activities")

    if missing_data:
        st.error(f"⚠️ البيانات التالية مفقودة: {', '.join(missing_data)}")
        st.info("يرجى إكمال المراحل السابقة أولاً")
        return

    # الحصول على الدرجة الكلية
    total_marks = float(course_data.get('total_course_marks', 100))

    # حساب درجات الأنشطة من النسب
    activity_marks = {}
    for activity in course_activities:
        activity_name = activity.get('assessment_task')
        percentage = float(activity.get('percentage', 0))
        activity_marks[activity_name] = (percentage / 100) * total_marks

    # الحصول على درجات CLOs
    clo_marks_data = {}
    for clo in course_clos:
        clo_code = clo.get('clo_code')
        clo_mark = float(clo.get('mark', 0))
        clo_marks_data[clo_code] = clo_mark

    # تحديد العلاقة بين CLOs والأنشطة (من المرحلة الأولى - assessment_methods)
    clo_activity_relations = get_clo_activity_relation(course_clos, course_activities)

    # الحصول على التوزيع المحفوظ
    saved_distribution = get_clos_activities_distribution(selected_course_id)

    # عرض رسالة النجاح
    if st.session_state.get('clos_activities_saved'):
        st.success("✅ تم حفظ التوزيع بنجاح!")
        st.session_state['clos_activities_saved'] = False

    # إنشاء قوائم الأسماء
    clo_codes = [clo.get('clo_code') for clo in course_clos]
    activity_names = [a.get('assessment_task') for a in course_activities]

    # عرض معلومات الملخص
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
                padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center;">
        <h4 style="color: white; margin: 0;">
            CLOs across Activities - {selected_course.get('course_code', '')}
        </h4>
        <p style="color: #fff3e0; margin: 5px 0 0 0;">
            Total Mark: {int(total_marks)} | CLOs: {len(course_clos)} | Activities: {len(course_activities)}
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.info("💡 الخلايا المظللة تعني أن المخرج غير مرتبط بهذا النشاط ولا تقبل إدخال درجة")

    # ======= بناء الجدول =======
    # حساب عرض الأعمدة
    col_widths = [0.4, 1.5] + [1.0] * len(clo_codes) + [0.8]

    # صف الرؤوس
    header_cols = st.columns(col_widths)

    with header_cols[0]:
        st.markdown("**No**")
    with header_cols[1]:
        st.markdown("**Activities**")

    for i, clo_code in enumerate(clo_codes):
        clo_mark = clo_marks_data.get(clo_code, 0)
        with header_cols[2 + i]:
            st.markdown(f"""
            <div style="background:#ffcc80;padding:5px;border-radius:5px;text-align:center;">
                <b>{clo_code}</b><br>
                <span style="color:#e65100;">{clo_mark:.0f}</span>
            </div>
            """, unsafe_allow_html=True)

    with header_cols[-1]:
        st.markdown("**Check**")

    st.markdown("---")

    # تخزين المدخلات
    all_inputs = {}

    # مجاميع CLOs
    clo_totals = {clo: 0.0 for clo in clo_codes}

    # صفوف الأنشطة
    for act_idx, activity in enumerate(course_activities):
        act_name = activity.get('assessment_task', '')
        act_mark = activity_marks.get(act_name, 0)

        # البيانات المحفوظة لهذا النشاط
        saved_act_data = saved_distribution.get(act_name, {})

        cols = st.columns(col_widths)

        # رقم النشاط
        with cols[0]:
            st.markdown(f"**{act_idx + 1}**")

        # اسم النشاط
        with cols[1]:
            st.markdown(f"{act_name}")

        # أعمدة CLOs
        activity_inputs = {}
        row_total = 0

        for i, clo_code in enumerate(clo_codes):
            with cols[2 + i]:
                # التحقق من الارتباط
                is_related = clo_activity_relations.get(clo_code, {}).get(act_name, True)

                if is_related:
                    # الخلية قابلة للإدخال
                    saved_val = float(saved_act_data.get(clo_code, 0))
                    clo_mark = clo_marks_data.get(clo_code, 0)

                    val = st.number_input(
                        f"v_{act_name}_{clo_code}",
                        min_value=0.0,
                        max_value=float(clo_mark) if clo_mark > 0 else float(total_marks),
                        value=saved_val,
                        step=1.0,
                        key=f"clo_act_{act_name}_{clo_code}",
                        label_visibility='collapsed'
                    )
                    activity_inputs[clo_code] = val
                    row_total += val
                    clo_totals[clo_code] += val
                else:
                    # الخلية غير قابلة للإدخال - مظللة
                    st.markdown("""
                    <div style="background:#bdbdbd;height:38px;border-radius:5px;"></div>
                    """, unsafe_allow_html=True)
                    activity_inputs[clo_code] = 0

        # عمود التحقق
        with cols[-1]:
            if abs(row_total - act_mark) < 0.1:
                st.markdown(f'<span style="background:#4caf50;color:white;padding:5px 10px;border-radius:3px;font-weight:bold;">Ok</span>', unsafe_allow_html=True)
            else:
                diff = act_mark - row_total
                st.markdown(f'<span style="background:#f44336;color:white;padding:5px 8px;border-radius:3px;font-weight:bold;">{diff:+.0f}</span>', unsafe_allow_html=True)

        all_inputs[act_name] = activity_inputs

    st.markdown("---")

    # ======= صف المجاميع =======
    total_cols = st.columns(col_widths)

    with total_cols[0]:
        st.markdown("")
    with total_cols[1]:
        st.markdown("**Total**")

    all_clos_valid = True
    for i, clo_code in enumerate(clo_codes):
        with total_cols[2 + i]:
            clo_total = clo_totals[clo_code]
            clo_mark = clo_marks_data.get(clo_code, 0)

            if abs(clo_total - clo_mark) < 0.1:
                st.markdown(f'<span style="background:#4caf50;color:white;padding:5px 10px;border-radius:3px;font-weight:bold;">{clo_total:.0f}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span style="background:#f44336;color:white;padding:5px 10px;border-radius:3px;font-weight:bold;">{clo_total:.0f}</span>', unsafe_allow_html=True)
                all_clos_valid = False

    with total_cols[-1]:
        st.markdown("")

    # ======= صف التحقق من CLOs =======
    check_cols = st.columns(col_widths)

    with check_cols[0]:
        st.markdown("")
    with check_cols[1]:
        st.markdown("**CLOs Check**")

    for i, clo_code in enumerate(clo_codes):
        with check_cols[2 + i]:
            clo_total = clo_totals[clo_code]
            clo_mark = clo_marks_data.get(clo_code, 0)

            if abs(clo_total - clo_mark) < 0.1:
                st.markdown("✅")
            else:
                diff = clo_mark - clo_total
                st.markdown(f"❌ ({diff:+.0f})")

    st.markdown("---")

    # ======= التحقق من صحة الأنشطة =======
    all_activities_valid = True
    for act_name in activity_names:
        expected = activity_marks.get(act_name, 0)
        actual = sum(all_inputs.get(act_name, {}).values())
        if abs(actual - expected) >= 0.1:
            all_activities_valid = False
            break

    # حالة الإكمال
    if all_clos_valid and all_activities_valid:
        st.success("✅ جميع البيانات صحيحة! يمكنك الحفظ والانتقال للخطوة التالية.")
    else:
        if not all_clos_valid:
            st.warning("⚠️ مجاميع بعض المخرجات لا تتطابق مع درجاتها المحددة")
        if not all_activities_valid:
            st.warning("⚠️ مجاميع بعض الأنشطة لا تتطابق مع درجاتها المحددة")

    st.markdown("---")

    # ======= أزرار الحفظ =======
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("💾 حفظ التوزيع / Save", type='primary', use_container_width=True):
            if save_clos_activities_distribution(selected_course_id, all_inputs):
                st.session_state['clos_activities_saved'] = True
                st.rerun()
            else:
                st.error("❌ حدث خطأ أثناء الحفظ")

    with col2:
        if st.button("📝 حفظ كمسودة / Draft", use_container_width=True):
            if save_clos_activities_distribution(selected_course_id, all_inputs):
                st.success("✅ تم حفظ المسودة")

    with col3:
        if st.button("🔄 إعادة تعيين / Reset", use_container_width=True):
            st.rerun()

    # ======= ملخص =======
    st.markdown("---")
    st.markdown("### 📋 Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Activities Summary")
        act_summary = []
        for act_name in activity_names:
            expected = activity_marks.get(act_name, 0)
            actual = sum(all_inputs.get(act_name, {}).values())
            status = "✅" if abs(actual - expected) < 0.1 else "❌"
            act_summary.append({
                'Activity': act_name[:20],
                'Expected': f"{expected:.0f}",
                'Actual': f"{actual:.0f}",
                'Status': status
            })
        df_act = pd.DataFrame(act_summary)
        st.dataframe(df_act, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("#### CLOs Summary")
        clo_summary = []
        for clo_code in clo_codes:
            expected = clo_marks_data.get(clo_code, 0)
            actual = clo_totals.get(clo_code, 0)
            status = "✅" if abs(actual - expected) < 0.1 else "❌"
            clo_summary.append({
                'CLO': clo_code,
                'Expected': f"{expected:.0f}",
                'Actual': f"{actual:.0f}",
                'Status': status
            })
        df_clo = pd.DataFrame(clo_summary)
        st.dataframe(df_clo, use_container_width=True, hide_index=True)

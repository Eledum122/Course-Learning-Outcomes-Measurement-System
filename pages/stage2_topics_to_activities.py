"""
المرحلة 2.3: توزيع درجات المواضيع على أنشطة التقييم
Stage 2.3: Topics Distribution on Activities
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
    """الحصول على بيانات المقرر"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            return course
    return {}


def get_topics_activities_distribution(course_id):
    """الحصول على توزيع درجات المواضيع على الأنشطة"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            return course.get('topics_activities_distribution', {})
    return {}


def save_topics_activities_distribution(course_id, distribution):
    """حفظ توزيع درجات المواضيع على الأنشطة"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            course['topics_activities_distribution'] = distribution
            course['last_updated'] = datetime.now().isoformat()
            break
    return save_courses_data(courses_data)


def calculate_activity_marks(activities, total_marks):
    """حساب درجات الأنشطة بناء على النسب المئوية"""
    activity_marks = {}
    for activity in activities:
        activity_name = activity.get('assessment_task')
        percentage = float(activity.get('percentage', 0))
        # الدرجة = النسبة * درجة المقرر / 100
        mark = (percentage / 100) * total_marks
        activity_marks[activity_name] = mark
    return activity_marks


def show_stage2_topics_to_activities(db: Database, user, lang: str):
    """عرض صفحة توزيع درجات المواضيع على أنشطة التقييم"""

    st.title("📝 المرحلة 2.3: توزيع درجات المواضيع على أنشطة التقييم")
    st.markdown("### Stage 2.3: Topics Distribution on Activities")

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
        key='topics_activities_dist_course_select'
    )

    selected_course_id = course_options[selected_course_name]
    selected_course = next((c for c in courses if c.get('course_id') == selected_course_id), None)

    st.markdown("---")

    # الحصول على البيانات
    course_topics = get_course_topics(selected_course_id)
    course_activities = get_course_activities(selected_course_id)
    course_data = get_course_data(selected_course_id)

    # التحقق من وجود البيانات
    if not course_topics:
        st.warning("⚠️ لا توجد موضوعات لهذا المقرر. يرجى إضافة موضوعات المقرر أولاً.")
        st.info("No topics defined for this course. Please add topics first.")
        return

    if not course_activities:
        st.warning("⚠️ لا توجد أنشطة تقييم لهذا المقرر. يرجى إضافة أنشطة التقييم أولاً.")
        st.info("No assessment activities defined. Please add activities first.")
        return

    # الحصول على الدرجة الكلية
    total_marks = float(course_data.get('total_course_marks', 100))

    # حساب درجات الأنشطة
    activity_marks = calculate_activity_marks(course_activities, total_marks)

    # عرض رسالة النجاح
    if st.session_state.get('topics_activities_dist_saved'):
        st.success("✅ تم حفظ التوزيع بنجاح / Distribution saved successfully")
        st.session_state['topics_activities_dist_saved'] = False

    # عرض معلومات الملخص
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center;">
        <h4 style="color: white; margin: 0;">
            Total Mark: {int(total_marks)} | Topics: {len(course_topics)} | Activities: {len(course_activities)}
        </h4>
    </div>
    """, unsafe_allow_html=True)

    # الحصول على التوزيع الحالي
    current_distribution = get_topics_activities_distribution(selected_course_id)

    # إنشاء أسماء الأنشطة
    activity_names = [a.get('assessment_task') for a in course_activities]

    # ======= بناء الجدول التفاعلي =======
    st.markdown("""
    <style>
    .header-row {
        background: #0066cc;
        color: white;
        font-weight: bold;
        padding: 10px;
        text-align: center;
        border-radius: 5px 5px 0 0;
    }
    .activity-header {
        background: #ffeb3b;
        color: black;
        font-weight: bold;
        padding: 8px;
        text-align: center;
    }
    .ok-status {
        background: #4caf50;
        color: white;
        padding: 5px 10px;
        border-radius: 3px;
        font-weight: bold;
    }
    .error-status {
        background: #f44336;
        color: white;
        padding: 5px 10px;
        border-radius: 3px;
        font-weight: bold;
    }
    .total-row {
        background: #4caf50;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # عرض رؤوس الأعمدة
    num_activities = len(activity_names)

    # حساب عرض الأعمدة - إضافة عمود Remark (ثابت من المرحلة السابقة)
    col_widths = [0.5, 2.5, 0.8] + [1.0] * num_activities + [1.0]
    header_cols = st.columns(col_widths)

    with header_cols[0]:
        st.markdown("**No.**")
    with header_cols[1]:
        st.markdown("**List of Topics**")
    with header_cols[2]:
        st.markdown("**Mark**")
        st.markdown("*(الدرجة)*")

    # أعمدة الأنشطة مع درجاتها
    for i, activity_name in enumerate(activity_names):
        with header_cols[3 + i]:
            activity_mark = activity_marks.get(activity_name, 0)
            short_name = activity_name[:12] + "..." if len(activity_name) > 12 else activity_name
            st.markdown(f"**{short_name}**")
            st.markdown(f"*{activity_mark:.0f}*")

    with header_cols[-1]:
        st.markdown("**Topics Checking**")

    st.markdown("---")

    # تخزين بيانات الإدخال
    distribution_inputs = {}
    topic_remarks = {}

    # الحصول على التوزيع المحفوظ سابقاً
    saved_distribution = get_topics_activities_distribution(selected_course_id)

    for topic in course_topics:
        topic_id = topic.get('topic_id')
        topic_number = topic.get('topic_number', '')
        topic_title = topic.get('topic_title', '')

        # الحصول على درجة الموضوع (remark_mark) من ملف المواضيع - تم تعديلها في المرحلة 2.2
        remark_value = float(topic.get('remark_mark', 0))

        # إذا لم يكن هناك remark_mark، استخدم calculated_mark
        if remark_value == 0:
            remark_value = float(topic.get('calculated_mark', 0))

        topic_remarks[topic_id] = remark_value

        # الحصول على التوزيع الحالي لهذا الموضوع
        current_topic_dist = current_distribution.get(topic_id, {})

        cols = st.columns(col_widths)

        with cols[0]:
            st.markdown(f"**{topic_number}**")

        with cols[1]:
            short_title = topic_title[:35] + "..." if len(topic_title) > 35 else topic_title
            st.markdown(f"{short_title}")

        # عمود Mark - ثابت (من المرحلة السابقة)
        with cols[2]:
            st.markdown(f"**{remark_value:.0f}**")

        # أعمدة الأنشطة
        topic_activity_inputs = {}
        for i, activity_name in enumerate(activity_names):
            with cols[3 + i]:
                current_value = float(current_topic_dist.get(activity_name, 0))

                value = st.number_input(
                    f"act_{topic_id}_{i}",
                    min_value=0.0,
                    max_value=float(remark_value) if remark_value > 0 else float(total_marks),
                    value=min(current_value, remark_value) if remark_value > 0 else current_value,
                    step=0.5,
                    key=f"topic_act_{topic_id}_{activity_name}",
                    label_visibility='collapsed'
                )
                topic_activity_inputs[activity_name] = value

        # حساب حالة الصف (مجموع الأنشطة = Mark)
        row_total = sum(topic_activity_inputs.values())

        with cols[-1]:
            if abs(row_total - remark_value) < 0.01:
                st.markdown('<span style="background:#4caf50;color:white;padding:5px 15px;border-radius:3px;font-weight:bold;">Ok</span>', unsafe_allow_html=True)
            else:
                diff = remark_value - row_total
                st.markdown(f'<span style="background:#f44336;color:white;padding:5px 10px;border-radius:3px;font-weight:bold;">Diff: {diff:+.1f}</span>', unsafe_allow_html=True)

        distribution_inputs[topic_id] = {
            'remark': remark_value,
            'activities': topic_activity_inputs
        }

    st.markdown("---")

    # ======= صف المجاميع =======
    total_cols = st.columns(col_widths)

    with total_cols[0]:
        st.markdown("")
    with total_cols[1]:
        st.markdown("**Total**")

    # حساب مجموع Remarks
    total_remarks = sum(topic_remarks.values())
    with total_cols[2]:
        # التحقق من أن مجموع Remarks = درجة المقرر
        if abs(total_remarks - total_marks) < 0.01:
            st.markdown(f'<span style="background:#4caf50;color:white;padding:5px 10px;border-radius:3px;font-weight:bold;">{total_remarks:.0f}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span style="background:#f44336;color:white;padding:5px 10px;border-radius:3px;font-weight:bold;">{total_remarks:.0f}</span>', unsafe_allow_html=True)

    # حساب مجاميع الأنشطة
    activity_totals = {name: 0 for name in activity_names}
    for topic_id, data in distribution_inputs.items():
        for activity_name, value in data.get('activities', {}).items():
            activity_totals[activity_name] += value

    for i, activity_name in enumerate(activity_names):
        with total_cols[3 + i]:
            st.markdown(f"**{activity_totals[activity_name]:.0f}**")

    with total_cols[-1]:
        st.markdown("")

    # ======= صف التحقق من الأنشطة =======
    check_cols = st.columns(col_widths)

    with check_cols[0]:
        st.markdown("")
    with check_cols[1]:
        st.markdown("**Activities Checking**")
    with check_cols[2]:
        st.markdown("")

    all_activities_valid = True
    for i, activity_name in enumerate(activity_names):
        with check_cols[3 + i]:
            expected_mark = activity_marks.get(activity_name, 0)
            actual_total = activity_totals.get(activity_name, 0)

            if abs(actual_total - expected_mark) < 0.01:
                st.markdown('<span style="background:#4caf50;color:white;padding:5px 15px;border-radius:3px;font-weight:bold;">Ok</span>', unsafe_allow_html=True)
            else:
                all_activities_valid = False
                diff = expected_mark - actual_total
                st.markdown(f'<span style="background:#f44336;color:white;padding:5px 10px;border-radius:3px;font-weight:bold;">{diff:+.1f}</span>', unsafe_allow_html=True)

    st.markdown("---")

    # ======= حالة الإكمال =======
    # التحقق من صحة مجموع Remarks
    remarks_valid = abs(total_remarks - total_marks) < 0.01

    # التحقق من صحة جميع الصفوف
    all_rows_valid = True
    for topic_id, data in distribution_inputs.items():
        topic_remark = data.get('remark', 0)
        row_total = sum(data.get('activities', {}).values())
        if abs(row_total - topic_remark) >= 0.01:
            all_rows_valid = False
            break

    if all_rows_valid and all_activities_valid and remarks_valid:
        st.success("✅ جميع البيانات صحيحة! يمكنك حفظ التوزيع.")
        st.success("All data is valid! You can save the distribution.")
    else:
        if not remarks_valid:
            st.warning(f"⚠️ مجموع درجات المواضيع ({total_remarks:.0f}) لا يساوي درجة المقرر ({total_marks:.0f})")
            st.warning(f"Total remarks ({total_remarks:.0f}) doesn't equal course mark ({total_marks:.0f})")
        if not all_rows_valid:
            st.warning("⚠️ بعض المواضيع لم يتم توزيع درجاتها بالكامل على الأنشطة")
            st.warning("Some topics have incomplete distribution across activities")
        if not all_activities_valid:
            st.warning("⚠️ مجاميع بعض الأنشطة لا تتطابق مع درجاتها المحددة")
            st.warning("Some activity totals don't match their expected marks")

    st.markdown("---")

    # ======= أزرار الحفظ =======
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("💾 حفظ التوزيع / Save Distribution", type='primary', use_container_width=True):
            # التحقق من صحة البيانات
            if not all_rows_valid or not all_activities_valid or not remarks_valid:
                st.error("⚠️ لا يمكن الحفظ: يرجى التأكد من صحة جميع البيانات")
                st.error("Cannot save: Please ensure all data is valid")
            else:
                # تحويل البيانات للحفظ - تضمين Remark مع الأنشطة
                save_data = {}
                for topic_id, data in distribution_inputs.items():
                    save_data[topic_id] = {
                        'remark': data.get('remark', 0),
                        **data.get('activities', {})
                    }

                if save_topics_activities_distribution(selected_course_id, save_data):
                    st.session_state['topics_activities_dist_saved'] = True
                    st.rerun()
                else:
                    st.error("❌ حدث خطأ أثناء الحفظ / Error saving distribution")

    with col2:
        if st.button("📝 حفظ كمسودة / Save as Draft", use_container_width=True):
            # حفظ بدون التحقق - تضمين Remark مع الأنشطة
            save_data = {}
            for topic_id, data in distribution_inputs.items():
                save_data[topic_id] = {
                    'remark': data.get('remark', 0),
                    **data.get('activities', {})
                }

            if save_topics_activities_distribution(selected_course_id, save_data):
                st.success("✅ تم حفظ المسودة / Draft saved")
            else:
                st.error("❌ حدث خطأ / Error")

    with col3:
        if st.button("🔄 إعادة تعيين / Reset", use_container_width=True):
            st.rerun()

    # ======= ملخص التوزيع =======
    st.markdown("---")
    st.markdown("### 📊 ملخص التوزيع / Distribution Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📋 درجات الأنشطة / Activity Marks")
        activity_summary = []
        for activity in course_activities:
            name = activity.get('assessment_task')
            percentage = activity.get('percentage', 0)
            mark = activity_marks.get(name, 0)
            actual = activity_totals.get(name, 0)
            status = "✅" if abs(actual - mark) < 0.01 else "❌"
            activity_summary.append({
                'النشاط / Activity': name,
                'النسبة / %': f"{percentage}%",
                'الدرجة / Mark': f"{mark:.0f}",
                'الفعلي / Actual': f"{actual:.0f}",
                'الحالة': status
            })

        df_activities = pd.DataFrame(activity_summary)
        st.dataframe(df_activities, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("#### 📈 إحصائيات / Statistics")

        valid_topics = sum(1 for topic_id, data in distribution_inputs.items()
                         if abs(sum(data.get('activities', {}).values()) - data.get('remark', 0)) < 0.01)

        valid_activities = sum(1 for name in activity_names
                              if abs(activity_totals.get(name, 0) - activity_marks.get(name, 0)) < 0.01)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("المواضيع الصحيحة", f"{valid_topics}/{len(course_topics)}")
        with col_b:
            st.metric("الأنشطة الصحيحة", f"{valid_activities}/{len(activity_names)}")
        with col_c:
            remarks_status = "✅" if remarks_valid else "❌"
            st.metric("مجموع Remarks", f"{total_remarks:.0f}/{total_marks:.0f} {remarks_status}")

        # نسبة الإكمال
        total_checks = len(course_topics) + len(activity_names) + 1  # +1 for remarks total
        valid_checks = valid_topics + valid_activities + (1 if remarks_valid else 0)
        completion = (valid_checks / total_checks) * 100
        st.progress(completion / 100)
        st.markdown(f"**نسبة الإكمال / Completion:** {completion:.0f}%")

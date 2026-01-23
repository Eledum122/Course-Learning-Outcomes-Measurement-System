"""
المرحلة 2.5: جدول المواصفات
Stage 2.5: Table of Specifications
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
    """الحصول على توزيع المخرجات على الأنشطة من المرحلة 2.4"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            return course.get('clos_activities_distribution', {})
    return {}


def get_topics_activities_distribution(course_id):
    """الحصول على توزيع المواضيع على الأنشطة من المرحلة 2.3"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            return course.get('topics_activities_distribution', {})
    return {}


def get_specifications_table_data(course_id):
    """الحصول على بيانات جدول المواصفات المحفوظة"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            return course.get('specifications_table_data', {})
    return {}


def save_specifications_table_data(course_id, specs_data):
    """حفظ بيانات جدول المواصفات"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            course['specifications_table_data'] = specs_data
            course['last_updated'] = datetime.now().isoformat()
            break
    return save_courses_data(courses_data)


def show_stage2_specifications_table(db: Database, user, lang: str):
    """عرض صفحة جدول المواصفات"""

    st.title("📋 المرحلة 2.5: جدول المواصفات")
    st.markdown("### Stage 2.5: Table of Specifications")

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
        key='specs_table_course_select'
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
    if not course_topics:
        missing_data.append("موضوعات المقرر / Topics")
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

    # الحصول على توزيع CLOs على الأنشطة من Stage 2.4
    clos_activities_dist = get_clos_activities_distribution(selected_course_id)

    # الحصول على توزيع المواضيع على الأنشطة من Stage 2.3
    topics_activities_dist = get_topics_activities_distribution(selected_course_id)

    # الحصول على البيانات المحفوظة
    saved_specs_data = get_specifications_table_data(selected_course_id)

    # عرض رسالة النجاح
    if st.session_state.get('specs_table_saved'):
        st.success("✅ تم حفظ جدول المواصفات بنجاح!")
        st.session_state['specs_table_saved'] = False

    # إنشاء قوائم الأسماء
    clo_codes = [clo.get('clo_code') for clo in course_clos]
    activity_names = [a.get('assessment_task') for a in course_activities]

    # الحصول على درجات CLOs
    clo_marks_data = {}
    for clo in course_clos:
        clo_code = clo.get('clo_code')
        clo_mark = float(clo.get('mark', 0))
        clo_marks_data[clo_code] = clo_mark

    # الحصول على الأنشطة المرتبطة بكل CLO
    clo_related_activities = {}
    for clo in course_clos:
        clo_code = clo.get('clo_code')
        clo_methods = clo.get('assessment_methods', [])
        clo_related_activities[clo_code] = [act for act in activity_names if act in clo_methods]

    # معلومات عن الجدول
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
                padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center;">
        <h4 style="color: white; margin: 0;">
            Table of Specifications - {selected_course.get('course_code', '')}
        </h4>
        <p style="color: #cce5ff; margin: 5px 0 0 0;">
            Topics: {len(course_topics)} | CLOs: {len(course_clos)} | Activities: {len(course_activities)} | Total: {total_marks:.0f}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ======= ملخص الأنشطة =======
    st.markdown("### 📊 ملخص الأنشطة / Activities Summary")
    act_cols = st.columns(len(course_activities))
    for i, act in enumerate(course_activities):
        act_name = act.get('assessment_task', '')
        act_mark = activity_marks.get(act_name, 0)
        with act_cols[i]:
            st.markdown(f"""
            <div style="background:#fff3e0;padding:10px;border-radius:8px;text-align:center;border:2px solid #ff9800;">
                <b style="color:#e65100;">{act_name}</b><br>
                <span style="font-size:20px;font-weight:bold;color:#ff6f00;">{act_mark:.0f}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # تخزين المدخلات
    all_inputs = {}

    # مجاميع للتحقق
    clo_activity_totals = {code: {act: 0.0 for act in activity_names} for code in clo_codes}

    # ======= عرض كل CLO في قسم منفصل =======
    st.markdown("### 📝 توزيع الدرجات على الأنشطة لكل ناتج تعلم")
    st.info("💡 إذا كان الناتج مرتبط بنشاط واحد فقط، يتم تعبئة الدرجات تلقائياً من عمود Dist")

    for clo in course_clos:
        clo_code = clo.get('clo_code')
        clo_mark = clo_marks_data.get(clo_code, 0)
        related_acts = clo_related_activities.get(clo_code, [])

        # فلترة المواضيع التي لها توزيع على هذا CLO فقط
        topics_with_dist = []
        for topic in course_topics:
            clo_distribution = topic.get('clo_distribution', {})
            dist_value = float(clo_distribution.get(clo_code, 0))
            if dist_value > 0:
                topics_with_dist.append(topic)

        if not topics_with_dist:
            st.warning(f"⚠️ لا توجد مواضيع مرتبطة بـ {clo_code}")
            continue

        # فلترة الأنشطة التي لها درجة > 0 لهذا CLO من Stage 2.4
        acts_with_marks = []
        for act in related_acts:
            clo_act_mark = float(clos_activities_dist.get(act, {}).get(clo_code, 0))
            if clo_act_mark > 0:
                acts_with_marks.append(act)

        if not acts_with_marks:
            st.warning(f"⚠️ لا توجد أنشطة بدرجات لـ {clo_code} - يرجى إكمال المرحلة 2.4")
            continue

        # تحديث single_activity بناءً على الأنشطة الفعلية
        single_activity = len(acts_with_marks) == 1

        # عنوان CLO - واضح ومبسط
        status_text = "[Auto]" if single_activity else "[Edit]"

        # عنوان القسم مع checkbox للطي
        col_title, col_check = st.columns([4, 1])
        with col_title:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 10px 15px; border-radius: 8px;">
                <span style="color: white; font-size: 16px; font-weight: bold;">
                    {clo_code} - Mark: {clo_mark:.0f} {status_text}
                </span>
            </div>
            """, unsafe_allow_html=True)
        with col_check:
            show_clo = st.checkbox("Show", value=False, key=f"show_{clo_code}")

        # بناء الجدول لهذا CLO
        num_related = len(acts_with_marks)
        col_widths = [0.3, 1.8, 0.4, 0.4] + [0.7] * num_related + [0.4, 0.3]

        # متغيرات للمجاميع
        clo_dist_total = 0
        clo_tot_total = 0

        if show_clo:
            # عرض وصف المخرج
            clo_description = clo.get('clo_description', '')
            if clo_description:
                st.markdown(f"**Description:** {clo_description[:60]}{'...' if len(clo_description) > 60 else ''}")
            # عرض تفاصيل الأنشطة
            acts_info = " | ".join([f"{act[:10]}({clos_activities_dist.get(act, {}).get(clo_code, 0):.0f})" for act in acts_with_marks])
            st.markdown(f"**Activities:** {acts_info}")
            st.caption(f"Topics: {len(topics_with_dist)} | Activities: {len(acts_with_marks)}")

            # صف الرؤوس
            header_cols = st.columns(col_widths)
            with header_cols[0]:
                st.markdown("**#**")
            with header_cols[1]:
                st.markdown("**Topic**")
            with header_cols[2]:
                st.markdown("**Mark**")
            with header_cols[3]:
                st.markdown("**Dist**")

            for i, act in enumerate(acts_with_marks):
                with header_cols[4 + i]:
                    short_act = act[:6] + ".." if len(act) > 6 else act
                    clo_act_mark = float(clos_activities_dist.get(act, {}).get(clo_code, 0))
                    st.markdown(f"**{short_act}**\n*({clo_act_mark:.0f})*")

            with header_cols[-2]:
                st.markdown("**Tot**")
            with header_cols[-1]:
                st.markdown("**V**")

            st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)

        # صفوف المواضيع - دائماً تحسب القيم
        for topic in topics_with_dist:
            topic_id = topic.get('topic_id')
            topic_title = topic.get('topic_title', '')
            topic_number = topic.get('topic_number', '')

            topic_mark = float(topic.get('remark_mark', 0))
            if topic_mark == 0:
                topic_mark = float(topic.get('calculated_mark', 0))

            clo_distribution = topic.get('clo_distribution', {})
            dist_value = float(clo_distribution.get(clo_code, 0))
            clo_dist_total += dist_value

            saved_topic = saved_specs_data.get(topic_id, {})

            topic_clo_activities = {}
            row_total = 0

            if show_clo:
                row_cols = st.columns(col_widths)
                with row_cols[0]:
                    st.markdown(f"**{topic_number}**")
                with row_cols[1]:
                    short_title = topic_title[:25] + "..." if len(topic_title) > 25 else topic_title
                    st.markdown(f"<span style='font-size:12px;'>{short_title}</span>", unsafe_allow_html=True)
                with row_cols[2]:
                    st.markdown(f"{topic_mark:.0f}")
                with row_cols[3]:
                    st.markdown(f"<span style='color:#9c27b0;font-weight:bold;'>{dist_value:.1f}</span>", unsafe_allow_html=True)

            for i, act in enumerate(acts_with_marks):
                saved_val = float(saved_topic.get(f'{clo_code}_{act}', 0))
                max_val = dist_value

                if single_activity:
                    default_val = dist_value
                else:
                    default_val = saved_val

                if show_clo:
                    with row_cols[4 + i]:
                        val = st.number_input(
                            f"inp_{topic_id}_{clo_code}_{act}",
                            min_value=0.0,
                            max_value=float(max_val),
                            value=min(default_val, max_val),
                            step=0.5,
                            key=f"spec_{topic_id}_{clo_code}_{act}",
                            label_visibility='collapsed',
                            disabled=single_activity
                        )
                else:
                    # استخدام session_state للحصول على القيمة المحفوظة
                    key = f"spec_{topic_id}_{clo_code}_{act}"
                    if key in st.session_state:
                        val = st.session_state[key]
                    else:
                        val = min(default_val, max_val)

                topic_clo_activities[act] = val
                row_total += val
                clo_activity_totals[clo_code][act] += val

            clo_tot_total += row_total

            if show_clo:
                with row_cols[-2]:
                    if abs(row_total - dist_value) < 0.1:
                        st.markdown(f"<span style='background:#4caf50;color:white;padding:2px 6px;border-radius:3px;'>{row_total:.1f}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='background:#f44336;color:white;padding:2px 6px;border-radius:3px;'>{row_total:.1f}</span>", unsafe_allow_html=True)
                with row_cols[-1]:
                    if abs(row_total - dist_value) < 0.1:
                        st.markdown("V")
                    else:
                        st.markdown("X")

            # تخزين البيانات
            if topic_id not in all_inputs:
                all_inputs[topic_id] = {}
            all_inputs[topic_id][clo_code] = {
                'dist': dist_value,
                'activities': topic_clo_activities,
                'tot': row_total
            }

        if show_clo:
            # صف المجاميع
            st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)
            total_row = st.columns(col_widths)

            with total_row[0]:
                st.markdown("")
            with total_row[1]:
                st.markdown("**Total**")
            with total_row[2]:
                st.markdown("")
            with total_row[3]:
                st.markdown(f"**{clo_dist_total:.0f}**")

            for i, act in enumerate(acts_with_marks):
                with total_row[4 + i]:
                    act_total = clo_activity_totals[clo_code][act]
                    clo_act_expected = float(clos_activities_dist.get(act, {}).get(clo_code, 0))
                    if abs(act_total - clo_act_expected) < 0.1:
                        st.markdown(f"<span style='background:#4caf50;color:white;padding:2px 6px;border-radius:3px;font-weight:bold;'>{act_total:.0f}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='background:#f44336;color:white;padding:2px 6px;border-radius:3px;font-weight:bold;'>{act_total:.0f}</span>", unsafe_allow_html=True)

            with total_row[-2]:
                if abs(clo_tot_total - clo_mark) < 0.1:
                    st.markdown(f"<span style='background:#4caf50;color:white;padding:3px 8px;border-radius:5px;font-weight:bold;'>{clo_tot_total:.0f}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='background:#f44336;color:white;padding:3px 8px;border-radius:5px;font-weight:bold;'>{clo_tot_total:.0f}</span>", unsafe_allow_html=True)

            with total_row[-1]:
                if abs(clo_tot_total - clo_mark) < 0.1:
                    st.markdown("V")
                else:
                    diff = clo_mark - clo_tot_total
                    st.markdown(f"X ({diff:+.0f})")

            # صف التحقق من الأنشطة
            check_row = st.columns(col_widths)
            with check_row[0]:
                st.markdown("")
            with check_row[1]:
                st.markdown("*Expected*")
            with check_row[2]:
                st.markdown("")
            with check_row[3]:
                st.markdown(f"*{clo_mark:.0f}*")

            for i, act in enumerate(acts_with_marks):
                with check_row[4 + i]:
                    clo_act_expected = float(clos_activities_dist.get(act, {}).get(clo_code, 0))
                    st.markdown(f"*{clo_act_expected:.0f}*")

            with check_row[-2]:
                st.markdown(f"*{clo_mark:.0f}*")
            with check_row[-1]:
                st.markdown("")

    st.markdown("---")

    # ======= ملخص التحقق النهائي =======
    st.markdown("### ✅ ملخص التحقق النهائي / Final Validation")

    all_clos_valid = True
    all_activities_valid = True

    # جدول ملخص CLOs
    st.markdown("#### 📊 نواتج التعلم / CLOs")
    clo_summary_data = []
    for clo_code in clo_codes:
        expected = clo_marks_data.get(clo_code, 0)
        actual = sum(clo_activity_totals[clo_code][act] for act in activity_names)
        diff = expected - actual
        status = "✅" if abs(diff) < 0.1 else "❌"
        if abs(diff) >= 0.1:
            all_clos_valid = False
        clo_summary_data.append({
            "CLO": clo_code,
            "Expected": f"{expected:.0f}",
            "Actual": f"{actual:.0f}",
            "Diff": f"{diff:+.0f}" if abs(diff) >= 0.1 else "0",
            "Status": status
        })

    import pandas as pd
    clo_df = pd.DataFrame(clo_summary_data)
    st.dataframe(clo_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # جدول ملخص الأنشطة
    st.markdown("#### 📊 الأنشطة / Activities")
    act_summary_data = []
    for act_name in activity_names:
        expected = activity_marks.get(act_name, 0)
        actual = sum(clo_activity_totals[clo_code][act_name] for clo_code in clo_codes)
        diff = expected - actual
        status = "✅" if abs(diff) < 0.1 else "❌"
        if abs(diff) >= 0.1:
            all_activities_valid = False
        act_summary_data.append({
            "Activity": act_name,
            "Expected": f"{expected:.0f}",
            "Actual": f"{actual:.0f}",
            "Diff": f"{diff:+.0f}" if abs(diff) >= 0.1 else "0",
            "Status": status
        })

    act_df = pd.DataFrame(act_summary_data)
    st.dataframe(act_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ======= جدول تحقق المواضيع مع الأنشطة (Stage 2.3) =======
    st.markdown("#### 📋 تحقق المواضيع × الأنشطة (Stage 2.3)")
    st.info("💡 هذا الجدول يقارن مجموع درجات كل موضوع على كل نشاط في جدول المواصفات مع التوزيع المحدد في Stage 2.3")

    # حساب مجموع درجات كل موضوع على كل نشاط من جدول المواصفات
    topic_activity_totals = {}  # {topic_id: {activity: total}}
    for topic_id, topic_data in all_inputs.items():
        if topic_id not in topic_activity_totals:
            topic_activity_totals[topic_id] = {act: 0.0 for act in activity_names}
        for clo_code, clo_data in topic_data.items():
            for act_name, act_val in clo_data.get('activities', {}).items():
                topic_activity_totals[topic_id][act_name] += act_val

    # بناء جدول التحقق
    topics_validation_data = []
    all_topics_valid = True

    for topic in course_topics:
        topic_id = topic.get('topic_id')
        topic_number = topic.get('topic_number', '')
        topic_title = topic.get('topic_title', '')[:20]

        # توزيع الموضوع على الأنشطة من Stage 2.3
        expected_dist = topics_activities_dist.get(topic_id, {})

        # المجاميع الفعلية من جدول المواصفات
        actual_totals = topic_activity_totals.get(topic_id, {})

        row = {"#": topic_number, "الموضوع": topic_title}
        topic_valid = True

        for act_name in activity_names:
            expected = float(expected_dist.get(act_name, 0))
            actual = float(actual_totals.get(act_name, 0))

            if expected > 0 or actual > 0:
                if abs(actual - expected) < 0.1:
                    row[act_name[:8]] = f"✅ {actual:.0f}"
                else:
                    row[act_name[:8]] = f"❌ {actual:.0f}/{expected:.0f}"
                    topic_valid = False
                    all_topics_valid = False
            else:
                row[act_name[:8]] = "-"

        row["الحالة"] = "✅" if topic_valid else "❌"
        topics_validation_data.append(row)

    topics_df = pd.DataFrame(topics_validation_data)
    st.dataframe(topics_df, use_container_width=True, hide_index=True)

    if not all_topics_valid:
        st.warning("⚠️ بعض المواضيع لا تتطابق مع توزيع Stage 2.3")

    st.markdown("---")

    # جدول تفصيلي: CLO x Activity
    st.markdown("#### 📋 مصفوفة CLO × Activity")
    matrix_data = []
    for clo_code in clo_codes:
        row = {"CLO": clo_code}
        for act_name in activity_names:
            actual = clo_activity_totals[clo_code][act_name]
            expected = float(clos_activities_dist.get(act_name, {}).get(clo_code, 0))
            if expected > 0:
                status = "✅" if abs(actual - expected) < 0.1 else f"{actual:.0f}/{expected:.0f}"
                row[act_name[:8]] = status
            else:
                row[act_name[:8]] = "-"
        matrix_data.append(row)

    matrix_df = pd.DataFrame(matrix_data)
    st.dataframe(matrix_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ======= أزرار الحفظ =======
    # التحقق من صحة جميع البيانات
    all_valid = all_clos_valid and all_activities_valid and all_topics_valid

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("💾 حفظ جدول المواصفات / Save", type='primary', use_container_width=True):
            # التحقق من صحة جميع البيانات قبل الحفظ
            if not all_valid:
                # عرض رسالة خطأ مفصلة
                error_msg = "❌ لا يمكن الحفظ! يوجد أخطاء في البيانات:\n"
                if not all_clos_valid:
                    error_msg += "\n• نواتج التعلم (CLOs) غير متطابقة"
                if not all_activities_valid:
                    error_msg += "\n• الأنشطة غير متطابقة"
                if not all_topics_valid:
                    error_msg += "\n• المواضيع × الأنشطة لا تتطابق مع Stage 2.3"
                st.error(error_msg)
            else:
                # تحويل البيانات للحفظ
                save_data = {}
                for topic_id, topic_data in all_inputs.items():
                    topic_save = {}
                    for clo_code, clo_data in topic_data.items():
                        for act_name, act_val in clo_data.get('activities', {}).items():
                            topic_save[f'{clo_code}_{act_name}'] = act_val
                    save_data[topic_id] = topic_save

                if save_specifications_table_data(selected_course_id, save_data):
                    st.session_state['specs_table_saved'] = True
                    st.rerun()
                else:
                    st.error("❌ حدث خطأ أثناء الحفظ")

    with col2:
        if st.button("📝 حفظ كمسودة / Draft", use_container_width=True):
            save_data = {}
            for topic_id, topic_data in all_inputs.items():
                topic_save = {}
                for clo_code, clo_data in topic_data.items():
                    for act_name, act_val in clo_data.get('activities', {}).items():
                        topic_save[f'{clo_code}_{act_name}'] = act_val
                save_data[topic_id] = topic_save

            if save_specifications_table_data(selected_course_id, save_data):
                st.success("✅ تم حفظ المسودة")

    with col3:
        if st.button("🔄 إعادة تعيين / Reset", use_container_width=True):
            st.rerun()

    # ======= حالة الإكمال =======
    st.markdown("---")

    if all_clos_valid and all_activities_valid and all_topics_valid:
        st.success("🎉 تهانينا! المرحلة الثانية مكتملة بنجاح!")
        st.balloons()
    else:
        missing = []
        if not all_clos_valid:
            missing.append("نواتج التعلم")
        if not all_activities_valid:
            missing.append("الأنشطة")
        if not all_topics_valid:
            missing.append("المواضيع × الأنشطة (Stage 2.3)")
        st.warning(f"⏳ يرجى إكمال توزيع الدرجات: {', '.join(missing)}")

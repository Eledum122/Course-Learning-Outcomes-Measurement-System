"""
المرحلة 2.2: توزيع درجات الموضوعات على مخرجات التعلم
Stage 2.2: Topics Distribution to CLOs
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from models.database import Database, UserRole
from translations import t
import math


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


def save_topics_data(data):
    """حفظ بيانات الموضوعات"""
    topics_file = Path(__file__).parent.parent / 'data' / 'course_topics.json'
    try:
        with open(topics_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def get_course_clos(course_id):
    """الحصول على مخرجات التعلم للمقرر"""
    clos_data = load_clos_data()
    clos = [clo for clo in clos_data.get('clos', []) if clo.get('course_id') == course_id]
    # ترتيب حسب المجال ثم الكود
    knowledge = sorted([c for c in clos if 'Knowledge' in c.get('domain', '') or 'المعارف' in c.get('domain', '')], key=lambda x: x.get('clo_code', ''))
    skills = sorted([c for c in clos if 'Skills' in c.get('domain', '') or 'المهارات' in c.get('domain', '')], key=lambda x: x.get('clo_code', ''))
    values = sorted([c for c in clos if 'Values' in c.get('domain', '') or 'القيم' in c.get('domain', '')], key=lambda x: x.get('clo_code', ''))
    return knowledge + skills + values


def get_course_topics(course_id):
    """الحصول على موضوعات المقرر"""
    topics_data = load_topics_data()
    topics = [t for t in topics_data.get('topics', []) if t.get('course_id') == course_id]
    return sorted(topics, key=lambda x: int(x.get('topic_number', 0)))


def get_course_info(course_id):
    """الحصول على معلومات المقرر"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            return course
    return {}


def calculate_topic_marks(topics, total_marks):
    """حساب درجة كل موضوع بناء على ساعات الاتصال"""
    total_hours = sum(float(t.get('contact_hours', 0)) for t in topics)
    if total_hours == 0:
        return {t.get('topic_id'): 0 for t in topics}

    # حساب الدرجات الأولية
    raw_marks = {}
    for topic in topics:
        hours = float(topic.get('contact_hours', 0))
        raw_marks[topic.get('topic_id')] = (hours / total_hours) * total_marks

    # تقريب الدرجات مع ضمان أن المجموع = الدرجة الكلية
    rounded_marks = {}
    total_rounded = 0

    for topic_id, mark in raw_marks.items():
        rounded = round(mark)
        rounded_marks[topic_id] = rounded
        total_rounded += rounded

    # تعديل الفرق
    diff = int(total_marks - total_rounded)
    if diff != 0:
        # ترتيب حسب الجزء العشري للتعديل
        sorted_by_decimal = sorted(raw_marks.items(), key=lambda x: x[1] - int(x[1]), reverse=(diff > 0))
        for i in range(abs(diff)):
            if i < len(sorted_by_decimal):
                topic_id = sorted_by_decimal[i][0]
                rounded_marks[topic_id] += 1 if diff > 0 else -1

    return rounded_marks


def save_topics_distribution(course_id, distribution_data):
    """حفظ توزيع درجات الموضوعات"""
    topics_data = load_topics_data()

    for topic in topics_data.get('topics', []):
        if topic.get('course_id') == course_id:
            topic_id = topic.get('topic_id')
            if topic_id in distribution_data:
                topic['calculated_mark'] = distribution_data[topic_id].get('calculated_mark', 0)
                topic['remark_mark'] = distribution_data[topic_id].get('remark_mark', 0)
                topic['clo_distribution'] = distribution_data[topic_id].get('clo_distribution', {})
                topic['last_updated'] = datetime.now().isoformat()

    topics_data['last_updated'] = datetime.now().isoformat()
    return save_topics_data(topics_data)


def show_stage2_topics_to_clos(db: Database, user, lang: str):
    """عرض صفحة توزيع درجات الموضوعات على مخرجات التعلم"""

    st.title("🔗 المرحلة 2.2: توزيع درجات الموضوعات على مخرجات التعلم")
    st.markdown("### Stage 2.2: Topics Distribution to CLOs")

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
        key='topics_clos_course_select'
    )

    selected_course_id = course_options[selected_course_name]
    selected_course = next((c for c in courses if c.get('course_id') == selected_course_id), None)

    st.markdown("---")

    # الحصول على البيانات
    course_clos = get_course_clos(selected_course_id)
    course_topics = get_course_topics(selected_course_id)
    course_info = get_course_info(selected_course_id)

    # التحقق من وجود البيانات
    if not course_clos:
        st.warning("⚠️ لا توجد مخرجات تعلم لهذا المقرر. يرجى إضافة مخرجات التعلم أولاً.")
        return

    if not course_topics:
        st.warning("⚠️ لا توجد موضوعات لهذا المقرر. يرجى إضافة موضوعات المقرر أولاً.")
        return

    # عرض رسالة النجاح
    if st.session_state.get('topics_distribution_saved'):
        st.success("✅ تم حفظ التوزيع بنجاح / Distribution saved successfully")
        st.session_state['topics_distribution_saved'] = False

    # الحصول على الدرجة الكلية
    total_course_marks = float(course_info.get('total_course_marks', 100))
    total_hours = sum(float(t.get('contact_hours', 0)) for t in course_topics)

    # حساب درجات الموضوعات
    calculated_marks = calculate_topic_marks(course_topics, total_course_marks)

    # عرض المعلومات الرئيسية
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center;">
        <h3 style="color: white; margin: 0;">
            Total Mark: {int(total_course_marks)} | Total Hours: {int(total_hours)}
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # إنشاء رؤوس الأعمدة للـ CLOs
    clo_codes = [clo.get('clo_code') for clo in course_clos]
    clo_marks = {clo.get('clo_code'): clo.get('mark', 0) for clo in course_clos}

    # إنشاء DataFrame للعرض والتحرير
    st.markdown("### 📊 جدول توزيع الدرجات / Marks Distribution Table")

    # تهيئة البيانات
    distribution_data = {}

    # إنشاء الجدول
    # رؤوس الأعمدة
    header_cols = st.columns([0.5, 3, 1, 1, 1] + [1] * len(clo_codes) + [1])

    with header_cols[0]:
        st.markdown("**No.**")
    with header_cols[1]:
        st.markdown("**List of Topics**")
    with header_cols[2]:
        st.markdown("**Hours**")
    with header_cols[3]:
        st.markdown("**Mark**")
    with header_cols[4]:
        st.markdown("**Remark**")

    for i, clo_code in enumerate(clo_codes):
        with header_cols[5 + i]:
            mark = clo_marks.get(clo_code, 0)
            st.markdown(f"**{clo_code}**")
            st.markdown(f"*{int(mark)}*")

    with header_cols[-1]:
        st.markdown("**Check**")

    st.markdown("---")

    # بيانات الصفوف
    clo_totals = {code: 0 for code in clo_codes}
    all_rows_valid = True

    for topic in course_topics:
        topic_id = topic.get('topic_id')
        topic_number = topic.get('topic_number', '')
        topic_title = topic.get('topic_title', '')
        contact_hours = float(topic.get('contact_hours', 0))

        # الدرجة المحسوبة
        calc_mark = calculated_marks.get(topic_id, 0)

        # الدرجة المعدلة (Remark)
        current_remark = topic.get('remark_mark', calc_mark)
        current_clo_dist = topic.get('clo_distribution', {})

        cols = st.columns([0.5, 3, 1, 1, 1] + [1] * len(clo_codes) + [1])

        with cols[0]:
            st.markdown(f"**{topic_number}**")

        with cols[1]:
            st.markdown(f"<small>{topic_title[:40]}{'...' if len(topic_title) > 40 else ''}</small>", unsafe_allow_html=True)

        with cols[2]:
            st.markdown(f"{int(contact_hours)}")

        with cols[3]:
            st.markdown(f"**{calc_mark}**")

        with cols[4]:
            remark = st.number_input(
                f"Remark {topic_number}",
                min_value=0.0,
                max_value=float(total_course_marks),
                value=float(current_remark),
                step=1.0,
                key=f"remark_{topic_id}",
                label_visibility='collapsed'
            )

        # توزيع على CLOs
        clo_inputs = {}
        row_total = 0

        for i, clo_code in enumerate(clo_codes):
            with cols[5 + i]:
                current_val = current_clo_dist.get(clo_code, 0)
                val = st.number_input(
                    f"{clo_code}_{topic_id}",
                    min_value=0.0,
                    max_value=float(remark),
                    value=float(current_val),
                    step=0.5,
                    key=f"clo_{clo_code}_{topic_id}",
                    label_visibility='collapsed'
                )
                clo_inputs[clo_code] = val
                row_total += val
                clo_totals[clo_code] += val

        # التحقق من صحة الصف
        with cols[-1]:
            if abs(row_total - remark) < 0.01:
                st.markdown("✅ **Ok**")
            else:
                st.markdown(f"⚠️ {row_total:.1f}")
                all_rows_valid = False

        # حفظ البيانات
        distribution_data[topic_id] = {
            'calculated_mark': calc_mark,
            'remark_mark': remark,
            'clo_distribution': clo_inputs
        }

    st.markdown("---")

    # صف الإجماليات
    total_cols = st.columns([0.5, 3, 1, 1, 1] + [1] * len(clo_codes) + [1])

    with total_cols[0]:
        st.markdown("")
    with total_cols[1]:
        st.markdown("**Total**")
    with total_cols[2]:
        st.markdown(f"**{int(total_hours)}**")

    total_remark = sum(d.get('remark_mark', 0) for d in distribution_data.values())
    with total_cols[3]:
        st.markdown(f"**{int(total_course_marks)}**")
    with total_cols[4]:
        if abs(total_remark - total_course_marks) < 0.01:
            st.markdown(f"**✅ {int(total_remark)}**")
        else:
            st.markdown(f"**⚠️ {total_remark:.1f}**")

    for i, clo_code in enumerate(clo_codes):
        with total_cols[5 + i]:
            expected = clo_marks.get(clo_code, 0)
            actual = clo_totals[clo_code]
            if abs(actual - expected) < 0.01:
                st.markdown(f"**{int(actual)}**")
            else:
                st.markdown(f"**{actual:.1f}**")

    st.markdown("---")

    # صف التحقق من CLOs
    check_cols = st.columns([0.5, 3, 1, 1, 1] + [1] * len(clo_codes) + [1])

    with check_cols[1]:
        st.markdown("**CLOs Checking**")

    all_clos_valid = True
    for i, clo_code in enumerate(clo_codes):
        with check_cols[5 + i]:
            expected = clo_marks.get(clo_code, 0)
            actual = clo_totals[clo_code]
            if abs(actual - expected) < 0.01:
                st.markdown("✅ **Ok**")
            else:
                st.markdown(f"⚠️ {actual:.1f}/{int(expected)}")
                all_clos_valid = False

    st.markdown("---")

    # أزرار الحفظ
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        can_save = all_rows_valid and all_clos_valid and abs(total_remark - total_course_marks) < 0.01

        if st.button("💾 حفظ التوزيع / Save Distribution", type='primary', use_container_width=True, disabled=not can_save):
            if save_topics_distribution(selected_course_id, distribution_data):
                st.session_state['topics_distribution_saved'] = True
                st.rerun()
            else:
                st.error("❌ حدث خطأ أثناء الحفظ / Error saving distribution")

        if not can_save:
            st.warning("⚠️ يرجى التأكد من صحة جميع القيم قبل الحفظ")

    with col2:
        if st.button("📝 حفظ كمسودة / Save as Draft", use_container_width=True):
            if save_topics_distribution(selected_course_id, distribution_data):
                st.success("✅ تم حفظ المسودة / Draft saved")

    with col3:
        if st.button("🔄 إعادة تعيين / Reset", use_container_width=True):
            st.rerun()

    # ملخص الحالة
    st.markdown("---")
    st.markdown("### 📋 ملخص الحالة / Status Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        if abs(total_remark - total_course_marks) < 0.01:
            st.success(f"✅ مجموع Remark صحيح: {int(total_remark)}/{int(total_course_marks)}")
        else:
            st.error(f"❌ مجموع Remark غير صحيح: {total_remark:.1f}/{int(total_course_marks)}")

    with col2:
        if all_rows_valid:
            st.success("✅ جميع الصفوف صحيحة")
        else:
            st.error("❌ بعض الصفوف غير صحيحة")

    with col3:
        if all_clos_valid:
            st.success("✅ جميع CLOs متطابقة")
        else:
            st.error("❌ بعض CLOs غير متطابقة")

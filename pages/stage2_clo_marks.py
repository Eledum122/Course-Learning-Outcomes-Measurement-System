"""
المرحلة 2.1: توزيع الدرجات على مخرجات التعلم
Stage 2.1: CLO Marks Distribution
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


def save_clos_data(data):
    """حفظ بيانات مخرجات التعلم"""
    clos_file = Path(__file__).parent.parent / 'data' / 'clos.json'
    try:
        with open(clos_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def get_course_clos(course_id):
    """الحصول على مخرجات التعلم للمقرر"""
    clos_data = load_clos_data()
    return [clo for clo in clos_data.get('clos', []) if clo.get('course_id') == course_id]


def get_course_info(course_id):
    """الحصول على معلومات المقرر"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            return course
    return {}


def save_course_marks_info(course_id, total_marks, passing_percentage):
    """حفظ معلومات درجات المقرر"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            course['total_course_marks'] = total_marks
            course['passing_percentage'] = passing_percentage
            course['last_updated'] = datetime.now().isoformat()
            break
    return save_courses_data(courses_data)


def save_clo_marks_data(clo_id, mark, criterion, target):
    """حفظ درجات مخرج تعلم واحد"""
    clos_data = load_clos_data()
    for clo in clos_data.get('clos', []):
        if clo.get('clo_id') == clo_id:
            clo['mark'] = mark
            clo['criterion_percentage'] = criterion
            clo['target_percentage'] = target
            clo['last_updated'] = datetime.now().isoformat()
            break
    clos_data['last_updated'] = datetime.now().isoformat()
    return save_clos_data(clos_data)


def show_stage2_clo_marks(db: Database, user, lang: str):
    """عرض صفحة توزيع درجات مخرجات التعلم"""

    st.title("📊 المرحلة 2.1: توزيع الدرجات على مخرجات التعلم")
    st.markdown("### Stage 2.1: CLO Marks Distribution")

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
        key='clo_marks_course_select'
    )

    selected_course_id = course_options[selected_course_name]
    selected_course = next((c for c in courses if c.get('course_id') == selected_course_id), None)

    if not selected_course:
        return

    st.markdown("---")

    # الحصول على مخرجات التعلم للمقرر
    course_clos = get_course_clos(selected_course_id)

    if not course_clos:
        st.warning("⚠️ لا توجد مخرجات تعلم لهذا المقرر. يرجى إضافة مخرجات التعلم أولاً.")
        st.info("No CLOs defined for this course. Please add CLOs first.")
        return

    # عرض رسالة النجاح
    if st.session_state.get('clo_marks_saved'):
        st.success("✅ تم حفظ البيانات بنجاح / Data saved successfully")
        st.session_state['clo_marks_saved'] = False

    # الحصول على معلومات المقرر الحالية
    course_info = get_course_info(selected_course_id)

    # ======= القسم الأول: معلومات المقرر =======
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: white; margin: 0; text-align: center;">
            📋 معلومات المقرر / Course Information
        </h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**عنوان المقرر / Course Title:**")
        st.info(f"{selected_course.get('course_title_ar', '')} / {selected_course.get('course_title_en', '')}")

    with col2:
        total_course_marks = st.number_input(
            "الدرجة الكلية للمقرر / Total Course Marks:",
            min_value=1.0,
            max_value=1000.0,
            value=float(course_info.get('total_course_marks', 100)),
            step=1.0,
            key='total_course_marks'
        )

    with col3:
        passing_percentage = st.number_input(
            "نسبة النجاح (%) / Passing Percentage:",
            min_value=1.0,
            max_value=100.0,
            value=float(course_info.get('passing_percentage', 60)),
            step=1.0,
            key='passing_percentage'
        )

    st.markdown("---")

    # ======= القسم الثاني: توزيع درجات CLOs =======
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: white; margin: 0; text-align: center;">
            📝 توزيع درجات مخرجات التعلم / CLO Marks Distribution
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # ترتيب CLOs حسب المجال
    knowledge_clos = [c for c in course_clos if 'Knowledge' in c.get('domain', '') or 'المعارف' in c.get('domain', '')]
    skills_clos = [c for c in course_clos if 'Skills' in c.get('domain', '') or 'المهارات' in c.get('domain', '')]
    values_clos = [c for c in course_clos if 'Values' in c.get('domain', '') or 'القيم' in c.get('domain', '')]

    # ترتيب حسب الكود
    all_sorted_clos = sorted(knowledge_clos, key=lambda x: x.get('clo_code', '')) + \
                      sorted(skills_clos, key=lambda x: x.get('clo_code', '')) + \
                      sorted(values_clos, key=lambda x: x.get('clo_code', ''))

    # إنشاء جدول للإدخال
    st.markdown("#### أدخل بيانات كل مخرج تعلم:")
    st.markdown("Enter data for each CLO:")

    # رؤوس الأعمدة
    header_cols = st.columns([1, 1.5, 3, 1.2, 1.2, 1.2])
    with header_cols[0]:
        st.markdown("**الرمز**")
        st.markdown("*Code*")
    with header_cols[1]:
        st.markdown("**المجال**")
        st.markdown("*Category*")
    with header_cols[2]:
        st.markdown("**الوصف**")
        st.markdown("*Description*")
    with header_cols[3]:
        st.markdown("**الدرجة**")
        st.markdown("*Mark*")
    with header_cols[4]:
        st.markdown("**معيار النجاح %**")
        st.markdown("*Criterion %*")
    with header_cols[5]:
        st.markdown("**المستهدف %**")
        st.markdown("*Target %*")

    st.markdown("---")

    # تخزين القيم المدخلة
    clo_inputs = {}

    for clo in all_sorted_clos:
        clo_id = clo.get('clo_id')
        clo_code = clo.get('clo_code', '')

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
        if len(desc) > 50:
            desc = desc[:50] + '...'

        # القيم الحالية
        current_mark = clo.get('mark', 0)
        current_criterion = clo.get('criterion_percentage', passing_percentage)
        current_target = clo.get('target_percentage', 70)

        cols = st.columns([1, 1.5, 3, 1.2, 1.2, 1.2])

        with cols[0]:
            st.markdown(f"**{clo_code}**")

        with cols[1]:
            st.markdown(f"<span style='color: {category_color}; font-weight: bold;'>{category}</span>", unsafe_allow_html=True)

        with cols[2]:
            st.markdown(f"<small>{desc}</small>", unsafe_allow_html=True)

        with cols[3]:
            mark = st.number_input(
                f"درجة {clo_code}",
                min_value=0.0,
                max_value=float(total_course_marks),
                value=float(current_mark),
                step=1.0,
                key=f"mark_{clo_id}",
                label_visibility='collapsed'
            )

        with cols[4]:
            criterion = st.number_input(
                f"معيار {clo_code}",
                min_value=float(passing_percentage),
                max_value=100.0,
                value=float(max(current_criterion, passing_percentage)),
                step=1.0,
                key=f"criterion_{clo_id}",
                label_visibility='collapsed'
            )

        with cols[5]:
            target = st.number_input(
                f"مستهدف {clo_code}",
                min_value=float(criterion),
                max_value=100.0,
                value=float(max(current_target, criterion)),
                step=1.0,
                key=f"target_{clo_id}",
                label_visibility='collapsed'
            )

        clo_inputs[clo_id] = {
            'mark': mark,
            'criterion': criterion,
            'target': target
        }

    st.markdown("---")

    # ======= حساب المجموع والتحقق =======
    total_marks_assigned = sum(data['mark'] for data in clo_inputs.values())

    # عرض حالة المجموع
    if total_marks_assigned == total_course_marks:
        st.success(f"✅ إجمالي الدرجات: {total_marks_assigned} / {total_course_marks} (صحيح)")
    elif total_marks_assigned < total_course_marks:
        st.warning(f"⚠️ إجمالي الدرجات: {total_marks_assigned} / {total_course_marks} (متبقي: {total_course_marks - total_marks_assigned})")
    else:
        st.error(f"❌ إجمالي الدرجات: {total_marks_assigned} / {total_course_marks} (تجاوز بـ: {total_marks_assigned - total_course_marks})")

    # شريط التقدم
    progress = min(total_marks_assigned / total_course_marks, 1.0) if total_course_marks > 0 else 0
    st.progress(progress)

    st.markdown("---")

    # ======= أزرار الحفظ والإلغاء =======
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("💾 حفظ جميع البيانات / Save All Data", type='primary', use_container_width=True):
            # التحقق من صحة المجموع
            if total_marks_assigned != total_course_marks:
                st.error(f"⚠️ لا يمكن الحفظ: مجموع الدرجات ({total_marks_assigned}) لا يساوي الدرجة الكلية ({total_course_marks})")
            else:
                # حفظ معلومات المقرر
                save_course_marks_info(selected_course_id, total_course_marks, passing_percentage)

                # حفظ درجات كل CLO
                for clo_id, data in clo_inputs.items():
                    save_clo_marks_data(clo_id, data['mark'], data['criterion'], data['target'])

                st.session_state['clo_marks_saved'] = True
                st.rerun()

    with col2:
        if st.button("🔄 إعادة تعيين / Reset", use_container_width=True):
            st.rerun()

    # ======= ملخص التوزيع =======
    st.markdown("---")
    st.markdown("### 📊 ملخص التوزيع / Distribution Summary")

    # حساب إجماليات حسب المجال
    knowledge_total = sum(clo_inputs.get(c.get('clo_id'), {}).get('mark', 0) for c in knowledge_clos)
    skills_total = sum(clo_inputs.get(c.get('clo_id'), {}).get('mark', 0) for c in skills_clos)
    values_total = sum(clo_inputs.get(c.get('clo_id'), {}).get('mark', 0) for c in values_clos)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📚 المعارف / Knowledge",
            f"{knowledge_total}",
            f"{len(knowledge_clos)} CLOs"
        )

    with col2:
        st.metric(
            "🛠️ المهارات / Skills",
            f"{skills_total}",
            f"{len(skills_clos)} CLOs"
        )

    with col3:
        st.metric(
            "💎 القيم / Values",
            f"{values_total}",
            f"{len(values_clos)} CLOs"
        )

    with col4:
        st.metric(
            "📊 الإجمالي / Total",
            f"{total_marks_assigned}",
            f"من {total_course_marks}"
        )

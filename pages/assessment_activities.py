"""
صفحة إدارة أنشطة التقييم ونسبها
Assessment Activities Management Page
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from models.database import Database, UserRole
from translations import t
import io


def load_courses_data():
    """تحميل بيانات المقررات من الملف"""
    courses_file = Path(__file__).parent.parent / 'data' / 'courses.json'

    if courses_file.exists():
        try:
            with open(courses_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"courses": []}
    else:
        return {"courses": []}


def save_courses_data(data):
    """حفظ بيانات المقررات إلى الملف"""
    courses_file = Path(__file__).parent.parent / 'data' / 'courses.json'

    try:
        with open(courses_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def load_clos_data():
    """تحميل بيانات مخرجات التعلم من الملف"""
    clos_file = Path(__file__).parent.parent / 'data' / 'clos.json'

    if clos_file.exists():
        try:
            with open(clos_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"clos": []}
    else:
        return {"clos": []}


def get_assessment_methods_from_clos(course_id):
    """استخراج طرق التقييم الفريدة من مخرجات التعلم للمقرر"""
    clos_data = load_clos_data()
    assessment_methods = set()

    for clo in clos_data.get('clos', []):
        if clo.get('course_id') == course_id:
            methods = clo.get('assessment_methods', [])
            for method in methods:
                assessment_methods.add(method)

    return list(assessment_methods)


def get_course_activities(course_id):
    """الحصول على أنشطة التقييم لمقرر معين"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            return course.get('assessment_activities', [])
    return []


def save_course_activities(course_id, activities):
    """حفظ أنشطة التقييم لمقرر معين"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            course['assessment_activities'] = activities
            course['last_updated'] = datetime.now().isoformat()
            break
    return save_courses_data(courses_data)


def show_assessment_activities(db: Database, user, lang: str):
    """عرض صفحة أنشطة التقييم"""

    is_rtl = lang == 'ar'

    st.title(f"📊 أنشطة التقييم ونسبها / Assessment Activities & Percentages")

    # تحميل المقررات
    all_courses = db.get_all_courses()
    all_programs = db.get_all_programs()

    # تصفية حسب الصلاحيات
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
        st.warning(f"⚠️ لا توجد مقررات متاحة / No courses available")
        return

    # اختيار المقرر
    course_options = {
        f"{c.get('course_code', '')} - {c.get('course_title_ar' if lang == 'ar' else 'course_title_en', '')}": c.get('course_id')
        for c in courses
    }

    selected_course_name = st.selectbox(
        "🎯 اختر المقرر / Select Course:",
        options=list(course_options.keys()),
        key='assessment_course_select'
    )

    selected_course_id = course_options[selected_course_name]
    selected_course = next((c for c in courses if c.get('course_id') == selected_course_id), None)

    if not selected_course:
        return

    st.markdown("---")

    # تحميل أنشطة التقييم من بيانات المقرر
    course_activities = get_course_activities(selected_course_id)

    # استخراج طرق التقييم من CLOs
    clo_assessment_methods = get_assessment_methods_from_clos(selected_course_id)

    # عرض طرق التقييم المستخرجة من CLOs إذا لم توجد أنشطة
    if not course_activities and clo_assessment_methods:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h3 style="color: white; margin: 0; text-align: center;">
                🔄 طرق التقييم المستخرجة من مخرجات التعلم / Assessment Methods from CLOs
            </h3>
        </div>
        """, unsafe_allow_html=True)

        st.info(f"ℹ️ تم العثور على {len(clo_assessment_methods)} طريقة تقييم من مخرجات التعلم. يمكنك استيرادها كأنشطة تقييم.")
        st.write("Found assessment methods from CLOs. You can import them as assessment activities.")

        # عرض طرق التقييم المستخرجة
        methods_text = ", ".join(clo_assessment_methods)
        st.markdown(f"""
        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
            <strong>📋 طرق التقييم / Assessment Methods:</strong><br>
            {methods_text}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("📥 استيراد كأنشطة تقييم / Import as Assessment Activities", type='primary', use_container_width=True):
            # تحويل طرق التقييم إلى أنشطة تقييم
            new_activities = []
            for idx, method in enumerate(clo_assessment_methods):
                new_activity = {
                    'activity_id': f"activity_{selected_course_id}_{idx + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'course_id': selected_course_id,
                    'assessment_task': method,
                    'week_due': '',
                    'percentage': 0.0,  # النسبة صفر - يجب تعديلها لاحقاً
                    'created_date': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'imported_from_clos': True
                }
                new_activities.append(new_activity)

            if save_course_activities(selected_course_id, new_activities):
                st.success(f"✅ تم استيراد {len(new_activities)} نشاط تقييم. يرجى تعديل النسب المئوية.")
                st.rerun()

        st.markdown("---")

    # عرض رسائل النجاح
    if st.session_state.get('activity_update_success'):
        st.success(f"✅ تم تحديث النشاط بنجاح / Activity updated successfully")
        st.session_state['activity_update_success'] = False

    if st.session_state.get('activity_delete_success'):
        st.success(f"✅ تم حذف النشاط بنجاح / Activity deleted successfully")
        st.session_state['activity_delete_success'] = False

    # تهيئة session_state للتعديل
    if 'editing_activity' not in st.session_state:
        st.session_state.editing_activity = None

    # قسم تعديل نشاط - يظهر فقط عند اختيار نشاط للتعديل
    if st.session_state.editing_activity:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;
                    border: 3px solid #ff4757;">
            <h3 style="color: white; margin: 0; text-align: center;">
                ✏️ Edit Activity / تعديل النشاط
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # إنشاء مفتاح ديناميكي للنموذج
        form_key_suffix = st.session_state.editing_activity.get('activity_id', 'edit')

        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.markdown('<p style="color: #9932CC; font-weight: bold; font-size: 16px;">Assessment Task / مهمة التقييم *</p>', unsafe_allow_html=True)
                # قائمة أنواع التقييم المحددة مسبقاً
                assessment_types = [
                    "First Exam / الاختبار الأول",
                    "Second Exam / الاختبار الثاني",
                    "Final Exam / الاختبار النهائي",
                    "Quizzes / اختبارات قصيرة",
                    "Assignments / الواجبات",
                    "Oral Presentation / العرض الشفهي",
                    "Lab Work / العمل المعملي",
                    "Project / المشروع",
                    "Research Paper / البحث",
                    "Participation / المشاركة",
                    "Other / أخرى"
                ]

                current_task = st.session_state.editing_activity.get('assessment_task', '')
                if current_task in assessment_types:
                    default_index = assessment_types.index(current_task)
                else:
                    default_index = len(assessment_types) - 1  # Other

                assessment_task = st.selectbox(
                    "Assessment Task",
                    options=assessment_types,
                    index=default_index,
                    key=f'assessment_task_select_{form_key_suffix}',
                    label_visibility='collapsed'
                )

                # إذا اختار "أخرى" يمكنه إدخال نص مخصص
                if assessment_task == "Other / أخرى":
                    custom_task = st.text_input(
                        "Custom Task Name",
                        value=st.session_state.editing_activity.get('assessment_task', '') if st.session_state.editing_activity.get('assessment_task') not in assessment_types else '',
                        key=f'custom_task_input_{form_key_suffix}',
                        placeholder="أدخل اسم النشاط / Enter activity name"
                    )
                    if custom_task:
                        assessment_task = custom_task

            with col2:
                st.markdown('<p style="color: #1E90FF; font-weight: bold; font-size: 16px;">Week Due / أسبوع التسليم</p>', unsafe_allow_html=True)
                week_due = st.text_input(
                    "Week Due",
                    value=st.session_state.editing_activity.get('week_due', ''),
                    key=f'week_due_input_{form_key_suffix}',
                    label_visibility='collapsed',
                    placeholder="Week 6 / الأسبوع 6"
                )

            with col3:
                st.markdown('<p style="color: #FF8C00; font-weight: bold; font-size: 16px;">Percentage / النسبة المئوية *</p>', unsafe_allow_html=True)
                percentage = st.number_input(
                    "Percentage",
                    min_value=0.0,
                    max_value=100.0,
                    step=1.0,
                    value=float(st.session_state.editing_activity.get('percentage', 0)),
                    key=f'percentage_input_{form_key_suffix}',
                    label_visibility='collapsed'
                )

            st.markdown("<br>", unsafe_allow_html=True)

            # أزرار الإجراءات - تحديث وإلغاء فقط
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("✏️ Update / تحديث", use_container_width=True, type='primary'):
                    if assessment_task and assessment_task != "Other / أخرى" and percentage > 0:
                        # تحديث النشاط
                        updated_activities = []
                        for activity in course_activities:
                            if activity.get('activity_id') == st.session_state.editing_activity.get('activity_id'):
                                activity['assessment_task'] = assessment_task
                                activity['week_due'] = week_due
                                activity['percentage'] = percentage
                                activity['last_updated'] = datetime.now().isoformat()
                            updated_activities.append(activity)

                        if save_course_activities(selected_course_id, updated_activities):
                            st.session_state['activity_update_success'] = True
                            st.session_state.editing_activity = None
                            st.rerun()
                    else:
                        st.error("⚠️ الرجاء ملء جميع الحقول المطلوبة / Please fill all required fields")

            with col2:
                if st.button("❌ Cancel / إلغاء", use_container_width=True):
                    st.session_state.editing_activity = None
                    st.rerun()

            with col3:
                # حذف النشاط مباشرة من نموذج التعديل
                if st.button("🗑️ Delete / حذف", use_container_width=True, type='secondary'):
                    st.session_state['show_activity_delete_confirmation'] = True
                    st.session_state['activity_to_delete'] = st.session_state.editing_activity
                    st.rerun()

        st.markdown("---")

    # عرض قائمة أنشطة التقييم
    st.markdown("""
    <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: white; margin: 0; text-align: center;">
            📋 Assessment Activities List / قائمة أنشطة التقييم
        </h3>
    </div>
    """, unsafe_allow_html=True)

    if course_activities:
        # عرض الجدول مع أزرار التحريك
        total_percentage = 0

        # إنشاء جدول HTML مخصص
        st.markdown("""
        <style>
        .activity-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .activity-table thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .activity-table th {
            padding: 15px;
            text-align: center;
            font-weight: 600;
        }
        .activity-table td {
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #e0e0e0;
        }
        .activity-table tr:hover {
            background: #f5f5f5;
        }
        .activity-row {
            cursor: pointer;
            transition: background 0.2s;
        }
        .activity-row:hover {
            background: #e3f2fd !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<table class="activity-table"><thead><tr><th>ترتيب / Order</th><th>Assessment Task / مهمة التقييم</th><th>Week Due / أسبوع التسليم</th><th>Percentage / النسبة</th></tr></thead><tbody>', unsafe_allow_html=True)

        for idx, activity in enumerate(course_activities):
            activity_id = activity.get('activity_id', idx)
            task_name = activity.get('assessment_task', '')
            week_due = activity.get('week_due', '')
            percentage = activity.get('percentage', 0)
            total_percentage += percentage

            # عرض صف النشاط مع أزرار التحريك
            col1, col2, col3, col4 = st.columns([1, 3, 2, 1])

            with col1:
                # أزرار التحريك
                subcol1, subcol2 = st.columns(2)
                with subcol1:
                    if idx > 0:  # يمكن التحريك لأعلى إذا لم يكن الأول
                        if st.button("⬆️", key=f"up_{activity_id}", help="تحريك لأعلى / Move Up"):
                            # تبديل مع النشاط السابق
                            course_activities[idx], course_activities[idx-1] = course_activities[idx-1], course_activities[idx]
                            save_course_activities(selected_course_id, course_activities)
                            st.rerun()
                    else:
                        st.write("")  # مسافة فارغة

                with subcol2:
                    if idx < len(course_activities) - 1:  # يمكن التحريك لأسفل إذا لم يكن الأخير
                        if st.button("⬇️", key=f"down_{activity_id}", help="تحريك لأسفل / Move Down"):
                            # تبديل مع النشاط التالي
                            course_activities[idx], course_activities[idx+1] = course_activities[idx+1], course_activities[idx]
                            save_course_activities(selected_course_id, course_activities)
                            st.rerun()
                    else:
                        st.write("")  # مسافة فارغة

            with col2:
                # النقر على النشاط للتعديل
                if st.button(f"📝 {task_name}", key=f"select_{activity_id}", use_container_width=True, help="انقر للتعديل / Click to Edit"):
                    st.session_state.editing_activity = activity
                    st.toast(f"🔄 جاري تحميل النشاط للتعديل...")
                    st.rerun()

            with col3:
                st.write(week_due)

            with col4:
                st.write(f"{percentage}%")

        st.markdown('</tbody></table>', unsafe_allow_html=True)

        # إجمالي النسب
        if total_percentage == 100:
            color = "#28a745"  # أخضر
            status = "✅"
        elif total_percentage > 100:
            color = "#dc3545"  # أحمر
            status = "⚠️"
        else:
            color = "#ffc107"  # أصفر
            status = "⏳"

        st.markdown(f"""
        <div style="background: #f0f8ff; padding: 15px; border-radius: 5px; margin-top: 10px;">
            <h4 style="margin: 0; text-align: center;">
                {status} إجمالي النسب / Total Percentage: <span style="color: {color}; font-size: 24px;">{total_percentage}%</span>
            </h4>
            <p style="text-align: center; color: #666; margin: 5px 0 0 0;">
                {"النسبة صحيحة / Correct percentage" if total_percentage == 100 else "يجب أن يكون الإجمالي 100% / Total must be 100%"}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # نافذة تأكيد الحذف
        if st.session_state.get('show_activity_delete_confirmation') and st.session_state.get('activity_to_delete'):
            activity_to_delete = st.session_state['activity_to_delete']
            st.markdown("---")
            st.warning(f"⚠️ **تأكيد الحذف / Confirm Delete**")
            st.write(f"هل أنت متأكد من حذف النشاط **{activity_to_delete.get('assessment_task', '')}**؟")
            st.write("Are you sure you want to delete this activity?")

            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                if st.button("✅ نعم، احذف / Yes, Delete", use_container_width=True, type='primary'):
                    # حذف النشاط
                    updated_activities = [a for a in course_activities if a.get('activity_id') != activity_to_delete.get('activity_id')]

                    if save_course_activities(selected_course_id, updated_activities):
                        st.session_state['activity_delete_success'] = True
                        st.session_state['show_activity_delete_confirmation'] = False
                        st.session_state['activity_to_delete'] = None
                        st.session_state.editing_activity = None  # إغلاق نموذج التعديل
                        st.rerun()

            with col2:
                if st.button("❌ إلغاء / Cancel", use_container_width=True):
                    st.session_state['show_activity_delete_confirmation'] = False
                    st.session_state['activity_to_delete'] = None
                    # Keep editing_activity so user can continue editing
                    st.rerun()

    else:
        st.info("ℹ️ لا توجد أنشطة تقييم مضافة لهذا المقرر / No assessment activities added for this course yet")


def create_excel_template():
    """إنشاء قالب Excel لأنشطة التقييم"""
    df = pd.DataFrame({
        'Assessment Task / مهمة التقييم': ['First Exam', 'Second Exam', 'Final Exam', 'Quizzes', 'Assignments', 'Oral Presentation'],
        'Week Due / أسبوع التسليم': ['Week 6', 'Week 11', 'End of semester', 'Week 5, 10', 'Week 4, 8', 'During semester'],
        'Percentage / النسبة': [20, 20, 40, 10, 5, 5]
    })

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Assessment Activities', index=False)

    output.seek(0)
    return output.getvalue()


def import_from_excel(uploaded_file, course_id):
    """استيراد أنشطة التقييم من ملف Excel"""
    try:
        df = pd.read_excel(uploaded_file)

        # التحقق من الأعمدة المطلوبة
        required_columns = ['Assessment Task / مهمة التقييم', 'Percentage / النسبة']

        if not all(col in df.columns for col in required_columns):
            st.error("⚠️ الملف لا يحتوي على الأعمدة المطلوبة / File doesn't contain required columns")
            return

        # إضافة الأنشطة الجديدة
        new_activities = []
        for idx, row in df.iterrows():
            week_due = row.get('Week Due / أسبوع التسليم', '') if 'Week Due / أسبوع التسليم' in df.columns else ''

            new_activity = {
                'activity_id': f"activity_{course_id}_{idx + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'course_id': course_id,
                'assessment_task': str(row['Assessment Task / مهمة التقييم']),
                'week_due': str(week_due) if pd.notna(week_due) else '',
                'percentage': float(row['Percentage / النسبة']),
                'created_date': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            new_activities.append(new_activity)

        if save_course_activities(course_id, new_activities):
            st.success(f"✅ تم استيراد {len(df)} نشاط بنجاح / Successfully imported {len(df)} activities")
            st.rerun()
        else:
            st.error("❌ حدث خطأ أثناء الحفظ / Error saving data")

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء الاستيراد / Error during import: {str(e)}")

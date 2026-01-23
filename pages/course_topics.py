"""
صفحة إدارة موضوعات المقرر
Course Topics Management Page
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from models.database import Database, UserRole
from translations import t
import io


def load_topics_data():
    """تحميل بيانات الموضوعات من الملف"""
    topics_file = Path(__file__).parent.parent / 'data' / 'course_topics.json'

    if topics_file.exists():
        try:
            with open(topics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"topics": [], "last_updated": datetime.now().isoformat()}
    else:
        return {"topics": [], "last_updated": datetime.now().isoformat()}


def save_topics_data(data):
    """حفظ بيانات الموضوعات إلى الملف"""
    topics_file = Path(__file__).parent.parent / 'data' / 'course_topics.json'

    try:
        with open(topics_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def show_course_topics(db: Database, user, lang: str):
    """عرض صفحة موضوعات المقرر"""

    is_rtl = lang == 'ar'

    st.title(f"📚 موضوعات المقرر / Course Topics")

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
        key='topic_course_select'
    )

    selected_course_id = course_options[selected_course_name]
    selected_course = next((c for c in courses if c.get('course_id') == selected_course_id), None)

    if not selected_course:
        return

    st.markdown("---")

    # تحميل الموضوعات
    topics_data = load_topics_data()
    all_topics = topics_data.get('topics', [])
    course_topics = [t for t in all_topics if t.get('course_id') == selected_course_id]

    # عرض رسائل النجاح
    if st.session_state.get('topic_add_success'):
        st.success(f"✅ تم إضافة الموضوع بنجاح / Topic added successfully")
        st.session_state['topic_add_success'] = False

    if st.session_state.get('topic_update_success'):
        st.success(f"✅ تم تحديث الموضوع بنجاح / Topic updated successfully")
        st.session_state['topic_update_success'] = False

    if st.session_state.get('topic_delete_success'):
        st.success(f"✅ تم حذف الموضوع بنجاح / Topic deleted successfully")
        st.session_state['topic_delete_success'] = False

    # تهيئة session_state للتعديل
    if 'editing_topic' not in st.session_state:
        st.session_state.editing_topic = None

    # قسم إضافة/تعديل موضوع
    if st.session_state.editing_topic:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;
                    border: 3px solid #ff4757; animation: pulse 2s infinite;">
            <h3 style="color: white; margin: 0; text-align: center;">
                ✏️ Edit Topic / تعديل الموضوع
            </h3>
            <p style="color: white; margin: 5px 0; text-align: center; font-size: 14px;">
                🔄 يتم الآن تعديل الموضوع رقم: {topic_num}
            </p>
        </div>
        """.format(topic_num=st.session_state.editing_topic.get('topic_number', '')), unsafe_allow_html=True)

        st.info(f"ℹ️ **تحذير:** أنت الآن في وضع التعديل للموضوع رقم **{st.session_state.editing_topic.get('topic_number', '')}**. اضغط على 'تحديث/Update' لحفظ التغييرات أو 'مسح/Clear' للإلغاء.")
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h3 style="color: white; margin: 0; text-align: center;">
                ➕ Add Topic / إضافة موضوع
            </h3>
        </div>
        """, unsafe_allow_html=True)

    # نموذج الإضافة/التعديل
    # إنشاء مفتاح ديناميكي للنموذج بناءً على حالة التعديل
    form_key_suffix = st.session_state.editing_topic.get('topic_id', 'new') if st.session_state.editing_topic else 'new'

    with st.container():
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            st.markdown('<p style="color: #1E90FF; font-weight: bold; font-size: 16px;">Topic Number / رقم الموضوع</p>', unsafe_allow_html=True)
            # عرض رقم الموضوع بشكل تلقائي (غير قابل للتعديل)
            if st.session_state.editing_topic:
                # عند التعديل، يظهر الرقم الحالي للموضوع
                topic_number = st.session_state.editing_topic.get('topic_number', '')
                st.markdown(f'<div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px; text-align: center; font-size: 20px; font-weight: bold; color: #1976d2;">{topic_number}</div>', unsafe_allow_html=True)
            else:
                # عند الإضافة، حساب الرقم التسلسلي التالي تلقائياً
                next_number = len(course_topics) + 1
                topic_number = str(next_number)
                st.markdown(f'<div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px; text-align: center; font-size: 20px; font-weight: bold; color: #388e3c;">{topic_number}</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<p style="color: #FF8C00; font-weight: bold; font-size: 16px;">Contact Hours / ساعات الاتصال</p>', unsafe_allow_html=True)
            contact_hours = st.number_input(
                "Contact Hours",
                min_value=0.0,
                max_value=100.0,
                step=0.5,
                value=float(st.session_state.editing_topic.get('contact_hours', 0)) if st.session_state.editing_topic else 0.0,
                key=f'contact_hours_input_{form_key_suffix}',
                label_visibility='collapsed'
            )

        with col3:
            st.markdown('<p style="color: #9932CC; font-weight: bold; font-size: 16px;">Topic Title / عنوان الموضوع</p>', unsafe_allow_html=True)
            topic_title = st.text_input(
                "Topic Title",
                value=st.session_state.editing_topic.get('topic_title', '') if st.session_state.editing_topic else '',
                key=f'topic_title_input_{form_key_suffix}',
                label_visibility='collapsed'
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # أزرار الإجراءات
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.session_state.editing_topic:
                if st.button("✏️ Update / تحديث", use_container_width=True, type='primary'):
                    if topic_title:
                        # تحديث الموضوع (الرقم يبقى كما هو)
                        for topic in all_topics:
                            if topic.get('topic_id') == st.session_state.editing_topic.get('topic_id'):
                                # الرقم لا يتغير عند التعديل
                                topic['contact_hours'] = contact_hours
                                topic['topic_title'] = topic_title
                                topic['last_updated'] = datetime.now().isoformat()
                                break

                        topics_data['topics'] = all_topics
                        topics_data['last_updated'] = datetime.now().isoformat()

                        if save_topics_data(topics_data):
                            st.session_state['topic_update_success'] = True
                            st.session_state.editing_topic = None
                            st.rerun()
                    else:
                        st.error("⚠️ الرجاء إدخال عنوان الموضوع / Please enter topic title")
            else:
                if st.button("➕ Add / إضافة", use_container_width=True, type='primary'):
                    if topic_title:
                        # حساب الرقم التسلسلي التالي تلقائياً
                        next_number = str(len(course_topics) + 1)

                        # إضافة موضوع جديد
                        new_topic = {
                            'topic_id': f"topic_{selected_course_id}_{next_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            'course_id': selected_course_id,
                            'topic_number': next_number,
                            'contact_hours': contact_hours,
                            'topic_title': topic_title,
                            'created_date': datetime.now().isoformat(),
                            'last_updated': datetime.now().isoformat()
                        }

                        all_topics.append(new_topic)
                        topics_data['topics'] = all_topics
                        topics_data['last_updated'] = datetime.now().isoformat()

                        if save_topics_data(topics_data):
                            st.session_state['topic_add_success'] = True
                            st.rerun()
                    else:
                        st.error("⚠️ الرجاء إدخال عنوان الموضوع / Please enter topic title")

        with col2:
            if st.button("🗑️ Clear / مسح", use_container_width=True):
                st.session_state.editing_topic = None
                st.rerun()

        with col3:
            # تحميل قالب Excel
            excel_template = create_excel_template()
            st.download_button(
                label="📥 Download Excel Template / تحميل قالب Excel",
                data=excel_template,
                file_name=f"topics_template_{selected_course.get('course_code', '')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with col4:
            # استيراد من Excel
            uploaded_file = st.file_uploader(
                "📤 Import from Excel / استيراد من Excel",
                type=['xlsx'],
                key='import_topics_excel',
                label_visibility='collapsed'
            )
            if uploaded_file:
                if st.button("📤 Import / استيراد", use_container_width=True, type='primary'):
                    import_from_excel(uploaded_file, selected_course_id, all_topics, topics_data)

    st.markdown("---")

    # عرض قائمة الموضوعات
    st.markdown("""
    <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: white; margin: 0; text-align: center;">
            📋 Topics List / قائمة الموضوعات
        </h3>
    </div>
    """, unsafe_allow_html=True)

    if course_topics:
        # إنشاء DataFrame
        topics_display = []
        # الفرز بشكل رقمي وليس أبجدي
        for topic in sorted(course_topics, key=lambda x: int(x.get('topic_number', '0'))):
            topics_display.append({
                'Number / الرقم': topic.get('topic_number', ''),
                'Title / العنوان': topic.get('topic_title', ''),
                'Contact Hours / ساعات الاتصال': topic.get('contact_hours', 0)
            })

        df = pd.DataFrame(topics_display)

        # عرض الجدول
        st.dataframe(df, use_container_width=True, hide_index=True)

        # إجمالي ساعات الاتصال
        total_hours = sum(t.get('contact_hours', 0) for t in course_topics)
        st.markdown(f"""
        <div style="background: #f0f8ff; padding: 15px; border-radius: 5px; margin-top: 10px;">
            <h4 style="margin: 0; text-align: center;">
                📊 إجمالي ساعات الاتصال / Total Contact Hours: <span style="color: #1E90FF;">{total_hours}</span>
            </h4>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # أزرار التعديل والحذف
        st.subheader("⚙️ إدارة الموضوعات / Manage Topics")

        # تحديد الموضوع للتعديل أو الحذف
        topic_options = {
            f"{t.get('topic_number', '')} - {t.get('topic_title', '')}": t
            for t in course_topics
        }

        selected_topic_name = st.selectbox(
            "اختر موضوع / Select Topic:",
            options=list(topic_options.keys()),
            key='manage_topic_select'
        )

        selected_topic = topic_options[selected_topic_name]

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✏️ تعديل / Edit", use_container_width=True, type='primary'):
                st.session_state.editing_topic = selected_topic
                st.toast(f"🔄 جاري تحميل الموضوع رقم {selected_topic.get('topic_number', '')} للتعديل...")
                st.rerun()

        with col2:
            if st.button("🗑️ حذف / Delete", use_container_width=True, type='secondary'):
                st.session_state['show_delete_confirmation'] = True
                st.session_state['topic_to_delete'] = selected_topic
                st.rerun()

        # نافذة تأكيد الحذف
        if st.session_state.get('show_delete_confirmation') and st.session_state.get('topic_to_delete'):
            topic_to_delete = st.session_state['topic_to_delete']
            st.markdown("---")
            st.warning(f"⚠️ **تأكيد الحذف / Confirm Delete**")
            st.write(f"هل أنت متأكد من حذف الموضوع رقم **{topic_to_delete.get('topic_number', '')}** - {topic_to_delete.get('topic_title', '')}؟")
            st.write("Are you sure you want to delete this topic?")

            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                if st.button("✅ نعم، احذف / Yes, Delete", use_container_width=True, type='primary'):
                    # حذف الموضوع
                    all_topics = [t for t in all_topics if t.get('topic_id') != topic_to_delete.get('topic_id')]

                    # إعادة ترقيم الموضوعات المتبقية لنفس المقرر بشكل تسلسلي
                    remaining_course_topics = [t for t in all_topics if t.get('course_id') == selected_course_id]
                    remaining_course_topics.sort(key=lambda x: int(x.get('topic_number', 0)))

                    # تحديث الأرقام بشكل تسلسلي
                    for idx, topic in enumerate(remaining_course_topics, start=1):
                        topic['topic_number'] = str(idx)
                        topic['last_updated'] = datetime.now().isoformat()

                    topics_data['topics'] = all_topics
                    topics_data['last_updated'] = datetime.now().isoformat()

                    if save_topics_data(topics_data):
                        st.session_state['topic_delete_success'] = True
                        st.session_state['show_delete_confirmation'] = False
                        st.session_state['topic_to_delete'] = None
                        st.rerun()

            with col2:
                if st.button("❌ إلغاء / Cancel", use_container_width=True):
                    st.session_state['show_delete_confirmation'] = False
                    st.session_state['topic_to_delete'] = None
                    st.rerun()

    else:
        st.info("ℹ️ لا توجد موضوعات مضافة لهذا المقرر / No topics added for this course yet")


def create_excel_template():
    """إنشاء قالب Excel للموضوعات"""
    # ملاحظة: رقم الموضوع سيتم إنشاؤه تلقائياً، لا حاجة لإدخاله
    df = pd.DataFrame({
        'Contact Hours / ساعات الاتصال': [3, 2, 4],
        'Topic Title / عنوان الموضوع': ['Introduction to Programming', 'Data Structures', 'Algorithms']
    })

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Course Topics', index=False)

    output.seek(0)
    return output.getvalue()


def import_from_excel(uploaded_file, course_id, all_topics, topics_data):
    """استيراد الموضوعات من ملف Excel"""
    try:
        df = pd.read_excel(uploaded_file)

        # التحقق من الأعمدة المطلوبة (رقم الموضوع الآن اختياري)
        required_columns = ['Contact Hours / ساعات الاتصال', 'Topic Title / عنوان الموضوع']

        if not all(col in df.columns for col in required_columns):
            st.error("⚠️ الملف لا يحتوي على الأعمدة المطلوبة / File doesn't contain required columns")
            return

        # حذف الموضوعات القديمة لنفس المقرر
        all_topics = [t for t in all_topics if t.get('course_id') != course_id]

        # إضافة الموضوعات الجديدة بأرقام تسلسلية تلقائية
        for idx, row in df.iterrows():
            new_topic = {
                'topic_id': f"topic_{course_id}_{idx + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'course_id': course_id,
                'topic_number': str(idx + 1),  # الرقم التسلسلي التلقائي
                'contact_hours': float(row['Contact Hours / ساعات الاتصال']),
                'topic_title': str(row['Topic Title / عنوان الموضوع']),
                'created_date': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            all_topics.append(new_topic)

        topics_data['topics'] = all_topics
        topics_data['last_updated'] = datetime.now().isoformat()

        if save_topics_data(topics_data):
            st.success(f"✅ تم استيراد {len(df)} موضوع بنجاح / Successfully imported {len(df)} topics")
            st.rerun()
        else:
            st.error("❌ حدث خطأ أثناء الحفظ / Error saving data")

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء الاستيراد / Error during import: {str(e)}")

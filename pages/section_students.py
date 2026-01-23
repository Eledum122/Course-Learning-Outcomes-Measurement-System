"""
إدارة طلاب الشعبة
Section Students Management
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from io import BytesIO
from models.database import Database, UserRole


# Student status options
STUDENT_STATUS_OPTIONS = {
    "Regular": "منتظم / Regular",
    "Dropped": "معتذر / Dropped",
    "Incomplete": "غير مكتمل / Incomplete",
    "Prohibited": "محروم / Prohibited"
}

STUDENT_STATUS_AR = {
    "Regular": "منتظم",
    "Dropped": "معتذر",
    "Incomplete": "غير مكتمل",
    "Prohibited": "محروم"
}


def load_section_students_data():
    """Load section students data"""
    students_file = Path(__file__).parent.parent / 'data' / 'section_students.json'
    if students_file.exists():
        try:
            with open(students_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"section_students": []}
    return {"section_students": []}


def save_section_students_data(data):
    """Save section students data"""
    students_file = Path(__file__).parent.parent / 'data' / 'section_students.json'
    try:
        data['last_updated'] = datetime.now().isoformat()
        with open(students_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def load_sections_data():
    """Load sections data"""
    sections_file = Path(__file__).parent.parent / 'data' / 'sections.json'
    if sections_file.exists():
        try:
            with open(sections_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"sections": []}
    return {"sections": []}


def load_courses_data():
    """Load courses data"""
    courses_file = Path(__file__).parent.parent / 'data' / 'courses.json'
    if courses_file.exists():
        try:
            with open(courses_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"courses": []}
    return {"courses": []}


def load_programs_data():
    """Load programs data"""
    programs_file = Path(__file__).parent.parent / 'data' / 'programs.json'
    if programs_file.exists():
        try:
            with open(programs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"programs": []}
    return {"programs": []}


def get_section_students(section_id):
    """Get students for a specific section"""
    data = load_section_students_data()
    students = [s for s in data.get('section_students', []) if s.get('section_id') == section_id]
    # Sort by sequence
    return sorted(students, key=lambda x: x.get('seq', 0))


def generate_excel_template():
    """Generate Excel template for student upload"""
    df = pd.DataFrame({
        'Seq.': [1, 2, 3],
        'Student No.': ['', '', ''],
        'Student Name': ['', '', ''],
        'Status': ['Regular', 'Regular', 'Regular']
    })

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Students')
    output.seek(0)
    return output


def resequence_students(students):
    """Resequence students to maintain 1, 2, 3... order"""
    for i, student in enumerate(students, 1):
        student['seq'] = i
    return students


def move_student(section_id, student_id, direction):
    """Move a student up or down in the list"""
    students_data = load_section_students_data()

    # Get students for this section
    section_studs = [s for s in students_data['section_students'] if s.get('section_id') == section_id]
    other_studs = [s for s in students_data['section_students'] if s.get('section_id') != section_id]

    # Sort by sequence
    section_studs = sorted(section_studs, key=lambda x: x.get('seq', 0))

    # Find the student index
    student_index = None
    for i, s in enumerate(section_studs):
        if s.get('student_record_id') == student_id:
            student_index = i
            break

    if student_index is None:
        return False

    # Calculate new index
    if direction == 'up' and student_index > 0:
        new_index = student_index - 1
    elif direction == 'down' and student_index < len(section_studs) - 1:
        new_index = student_index + 1
    else:
        return False

    # Swap students
    section_studs[student_index], section_studs[new_index] = section_studs[new_index], section_studs[student_index]

    # Resequence
    section_studs = resequence_students(section_studs)

    # Update data
    students_data['section_students'] = other_studs + section_studs

    return save_section_students_data(students_data)


def show_section_students(db: Database, user, lang: str):
    """Display Section Students Management page"""

    st.title("Section Students / طلاب الشعبة")
    st.caption("Manage students enrolled in each section")

    # Load data
    sections_data = load_sections_data()
    sections = sections_data.get('sections', [])
    programs_data = load_programs_data()
    programs = programs_data.get('programs', [])
    courses_data = load_courses_data()
    courses = courses_data.get('courses', [])

    if not sections:
        st.warning("No sections found. Please create sections first.")
        return

    # Show success/error messages
    if st.session_state.get('students_message'):
        msg_type, msg_text = st.session_state.students_message
        if msg_type == 'success':
            st.success(msg_text)
        elif msg_type == 'error':
            st.error(msg_text)
        st.session_state.students_message = None

    # ===============================
    # Section 1: Select Section
    # ===============================
    st.markdown("### 1. Select Section / اختر الشعبة")

    col1, col2 = st.columns(2)

    with col1:
        # Create section options with course code, section number, and semester
        section_options = ["-- Select Section --"]
        section_map = {}

        for s in sections:
            course_code = s.get('course_code', '')
            section_num = s.get('section_number', '')
            semester_code = s.get('semester_code', '')
            year = s.get('academic_year', '')
            gender = s.get('gender', '').split(' / ')[0] if ' / ' in s.get('gender', '') else s.get('gender', '')

            option_text = f"{course_code} - Sec {section_num} ({year}/{semester_code}) - {gender}"
            section_options.append(option_text)
            section_map[option_text] = s

        selected_section_display = st.selectbox("Section / الشعبة", section_options, key="student_section_select")

        selected_section = None
        if selected_section_display != "-- Select Section --":
            selected_section = section_map.get(selected_section_display)

    with col2:
        if selected_section:
            st.info(f"""
            **Course:** {selected_section.get('course_code')}
            **Section:** {selected_section.get('section_number')}
            **Semester:** {selected_section.get('academic_year')} - {selected_section.get('semester_code')}
            """)

    if not selected_section:
        st.info("Please select a section to manage students")
        return

    section_id = selected_section.get('section_id')

    st.markdown("---")

    # ===============================
    # Section 2: Upload Excel Template
    # ===============================
    st.markdown("### 2. Upload Students / رفع قائمة الطلاب")

    col_upload1, col_upload2 = st.columns([1, 1])

    with col_upload1:
        # Download template button
        template_file = generate_excel_template()
        st.download_button(
            label="Download Template / تحميل القالب",
            data=template_file,
            file_name="students_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col_upload2:
        # Upload file
        uploaded_file = st.file_uploader(
            "Upload Excel File / رفع ملف Excel",
            type=['xlsx', 'xls'],
            key="students_upload"
        )

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)

            # Validate columns
            required_cols = ['Seq.', 'Student No.', 'Student Name', 'Status']
            if not all(col in df.columns for col in required_cols):
                st.error("Invalid file format. Please use the template.")
            else:
                st.markdown("**Preview:**")
                st.dataframe(df.head(10), use_container_width=True)

                if st.button("Import Students / استيراد الطلاب", type="primary"):
                    students_data = load_section_students_data()

                    # Remove existing students for this section
                    students_data['section_students'] = [
                        s for s in students_data['section_students']
                        if s.get('section_id') != section_id
                    ]

                    # Add new students
                    for idx, row in df.iterrows():
                        student_no = str(row.get('Student No.', '')).strip()
                        student_name = str(row.get('Student Name', '')).strip()
                        status = str(row.get('Status', 'Regular')).strip()

                        if student_no and student_name:
                            # Validate status
                            if status not in STUDENT_STATUS_OPTIONS:
                                status = 'Regular'

                            new_student = {
                                "student_record_id": f"stud_{section_id}_{student_no}",
                                "section_id": section_id,
                                "seq": idx + 1,
                                "student_no": student_no,
                                "student_name": student_name,
                                "status": status,
                                "created_at": datetime.now().isoformat()
                            }
                            students_data['section_students'].append(new_student)

                    if save_section_students_data(students_data):
                        st.session_state.students_message = ('success', f"Imported {len(df)} students successfully!")
                        st.rerun()
                    else:
                        st.session_state.students_message = ('error', "Error importing students!")
                        st.rerun()

        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

    st.markdown("---")

    # ===============================
    # Section 3: Students List
    # ===============================
    st.markdown("### 3. Students List / قائمة الطلاب")

    section_students = get_section_students(section_id)

    # Add new student form - using toggle instead of expander to avoid UI issues
    if 'show_add_student_form' not in st.session_state:
        st.session_state.show_add_student_form = False

    add_btn_col1, add_btn_col2 = st.columns([1, 4])
    with add_btn_col1:
        if st.button("➕ Add New Student", use_container_width=True):
            st.session_state.show_add_student_form = not st.session_state.show_add_student_form
            st.rerun()

    if st.session_state.show_add_student_form:
        st.markdown("#### إضافة طالب جديد")
        add_col1, add_col2, add_col3 = st.columns([1, 2, 1])

        with add_col1:
            new_student_no = st.text_input("Student No. / رقم الطالب", key="new_student_no")
        with add_col2:
            new_student_name = st.text_input("Student Name / اسم الطالب", key="new_student_name")
        with add_col3:
            new_status = st.selectbox(
                "Status / الحالة",
                options=list(STUDENT_STATUS_OPTIONS.keys()),
                format_func=lambda x: STUDENT_STATUS_OPTIONS[x],
                key="new_student_status"
            )

        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
        with btn_col1:
            if st.button("Add Student / إضافة", type="primary", use_container_width=True):
                if not new_student_no or not new_student_name:
                    st.error("Please enter student number and name")
                else:
                    # Check for duplicate
                    existing = [s for s in section_students if s.get('student_no') == new_student_no]
                    if existing:
                        st.error("Student number already exists in this section")
                    else:
                        students_data = load_section_students_data()

                        new_seq = len(section_students) + 1
                        new_student = {
                            "student_record_id": f"stud_{section_id}_{new_student_no}",
                            "section_id": section_id,
                            "seq": new_seq,
                            "student_no": new_student_no,
                            "student_name": new_student_name,
                            "status": new_status,
                            "created_at": datetime.now().isoformat()
                        }
                        students_data['section_students'].append(new_student)

                        if save_section_students_data(students_data):
                            st.session_state.show_add_student_form = False
                            st.session_state.students_message = ('success', f"Student {new_student_name} added successfully!")
                            st.rerun()
                        else:
                            st.session_state.students_message = ('error', "Error adding student!")
                            st.rerun()
        with btn_col2:
            if st.button("Cancel / إلغاء", use_container_width=True):
                st.session_state.show_add_student_form = False
                st.rerun()

        st.markdown("---")

    # Display students table
    if section_students:
        st.markdown(f"**Total Students: {len(section_students)}**")

        # Header
        header_cols = st.columns([0.4, 0.5, 1.3, 2.5, 1.3, 1])
        with header_cols[0]:
            st.markdown("**Move**")
        with header_cols[1]:
            st.markdown("**Seq.**")
        with header_cols[2]:
            st.markdown("**Student No.**")
        with header_cols[3]:
            st.markdown("**Student Name**")
        with header_cols[4]:
            st.markdown("**Status**")
        with header_cols[5]:
            st.markdown("**Actions**")

        st.markdown("---")

        # Initialize edit state
        if 'editing_student_id' not in st.session_state:
            st.session_state.editing_student_id = None

        total_students = len(section_students)

        for idx, student in enumerate(section_students):
            student_id = student.get('student_record_id')
            is_editing = st.session_state.editing_student_id == student_id
            current_seq = student.get('seq', idx + 1)

            row_cols = st.columns([0.4, 0.5, 1.3, 2.5, 1.3, 1])

            # Move buttons column
            with row_cols[0]:
                move_col1, move_col2 = st.columns(2)
                with move_col1:
                    # Up button - disabled if first student
                    if current_seq > 1:
                        if st.button("▲", key=f"up_{student_id}", use_container_width=True):
                            if move_student(section_id, student_id, 'up'):
                                st.rerun()
                    else:
                        st.button("▲", key=f"up_{student_id}", use_container_width=True, disabled=True)
                with move_col2:
                    # Down button - disabled if last student
                    if current_seq < total_students:
                        if st.button("▼", key=f"down_{student_id}", use_container_width=True):
                            if move_student(section_id, student_id, 'down'):
                                st.rerun()
                    else:
                        st.button("▼", key=f"down_{student_id}", use_container_width=True, disabled=True)

            with row_cols[1]:
                st.markdown(f"**{current_seq}**")

            with row_cols[2]:
                if is_editing:
                    edit_student_no = st.text_input(
                        "No",
                        value=student.get('student_no', ''),
                        key=f"edit_no_{student_id}",
                        label_visibility="collapsed"
                    )
                else:
                    st.markdown(student.get('student_no', ''))

            with row_cols[3]:
                if is_editing:
                    edit_student_name = st.text_input(
                        "Name",
                        value=student.get('student_name', ''),
                        key=f"edit_name_{student_id}",
                        label_visibility="collapsed"
                    )
                else:
                    st.markdown(student.get('student_name', ''))

            with row_cols[4]:
                if is_editing:
                    current_status = student.get('status', 'Regular')
                    status_index = list(STUDENT_STATUS_OPTIONS.keys()).index(current_status) if current_status in STUDENT_STATUS_OPTIONS else 0
                    edit_status = st.selectbox(
                        "Status",
                        options=list(STUDENT_STATUS_OPTIONS.keys()),
                        format_func=lambda x: STUDENT_STATUS_AR.get(x, x),
                        index=status_index,
                        key=f"edit_status_{student_id}",
                        label_visibility="collapsed"
                    )
                else:
                    status = student.get('status', 'Regular')
                    status_color = {
                        'Regular': '#28a745',
                        'Dropped': '#ffc107',
                        'Incomplete': '#17a2b8',
                        'Prohibited': '#dc3545'
                    }.get(status, '#6c757d')
                    st.markdown(f"<span style='color: {status_color}; font-weight: bold;'>{STUDENT_STATUS_AR.get(status, status)}</span>", unsafe_allow_html=True)

            with row_cols[5]:
                if is_editing:
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("Save", key=f"save_{student_id}", use_container_width=True):
                            # Save changes
                            students_data = load_section_students_data()
                            for s in students_data['section_students']:
                                if s.get('student_record_id') == student_id:
                                    s['student_no'] = st.session_state.get(f"edit_no_{student_id}", s['student_no'])
                                    s['student_name'] = st.session_state.get(f"edit_name_{student_id}", s['student_name'])
                                    s['status'] = st.session_state.get(f"edit_status_{student_id}", s['status'])
                                    s['updated_at'] = datetime.now().isoformat()
                                    break

                            if save_section_students_data(students_data):
                                st.session_state.editing_student_id = None
                                st.session_state.students_message = ('success', "Student updated!")
                                st.rerun()

                    with btn_col2:
                        if st.button("Cancel", key=f"cancel_{student_id}", use_container_width=True):
                            st.session_state.editing_student_id = None
                            st.rerun()
                else:
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("Edit", key=f"edit_{student_id}", use_container_width=True):
                            st.session_state.editing_student_id = student_id
                            st.rerun()
                    with btn_col2:
                        if st.button("Del", key=f"del_{student_id}", use_container_width=True):
                            st.session_state.delete_student_id = student_id

        # Delete confirmation
        if st.session_state.get('delete_student_id'):
            delete_id = st.session_state.delete_student_id
            student_to_delete = next((s for s in section_students if s.get('student_record_id') == delete_id), None)

            if student_to_delete:
                st.warning(f"Are you sure you want to delete **{student_to_delete.get('student_name')}** ({student_to_delete.get('student_no')})?")

                del_col1, del_col2, del_col3 = st.columns([1, 1, 2])
                with del_col1:
                    if st.button("Yes, Delete", type="primary", key="confirm_del"):
                        students_data = load_section_students_data()

                        # Remove student
                        students_data['section_students'] = [
                            s for s in students_data['section_students']
                            if s.get('student_record_id') != delete_id
                        ]

                        # Resequence remaining students
                        section_studs = [s for s in students_data['section_students'] if s.get('section_id') == section_id]
                        section_studs = resequence_students(sorted(section_studs, key=lambda x: x.get('seq', 0)))

                        # Update in data
                        other_studs = [s for s in students_data['section_students'] if s.get('section_id') != section_id]
                        students_data['section_students'] = other_studs + section_studs

                        if save_section_students_data(students_data):
                            st.session_state.delete_student_id = None
                            st.session_state.students_message = ('success', "Student deleted and list resequenced!")
                            st.rerun()

                with del_col2:
                    if st.button("Cancel", key="cancel_del"):
                        st.session_state.delete_student_id = None
                        st.rerun()

        st.markdown("---")

        # Export to Excel
        if st.button("Export to Excel / تصدير إلى Excel", use_container_width=True):
            export_data = []
            for s in section_students:
                export_data.append({
                    'Seq.': s.get('seq'),
                    'Student No.': s.get('student_no'),
                    'Student Name': s.get('student_name'),
                    'Status': s.get('status')
                })

            df_export = pd.DataFrame(export_data)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Students')
            output.seek(0)

            st.download_button(
                label="Download Excel File",
                data=output,
                file_name=f"students_{selected_section.get('course_code')}_{selected_section.get('section_number')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:
        st.info("No students in this section. Add students manually or upload an Excel file.")

    # Summary by status
    if section_students:
        st.markdown("---")
        st.markdown("### Summary / ملخص")

        status_counts = {}
        for s in section_students:
            status = s.get('status', 'Regular')
            status_counts[status] = status_counts.get(status, 0) + 1

        sum_cols = st.columns(4)
        for i, (status, label) in enumerate(STUDENT_STATUS_OPTIONS.items()):
            with sum_cols[i]:
                count = status_counts.get(status, 0)
                st.metric(STUDENT_STATUS_AR.get(status, status), count)

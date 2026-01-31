"""
Sections Management Page
إدارة الشعب الدراسية
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from models.database import Database, UserRole
from utils.permissions import get_permissions_helper


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


def save_sections_data(data):
    """Save sections data"""
    sections_file = Path(__file__).parent.parent / 'data' / 'sections.json'
    try:
        with open(sections_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def load_coordinators_data():
    """Load course coordinators data"""
    coordinators_file = Path(__file__).parent.parent / 'data' / 'course_coordinators.json'
    if coordinators_file.exists():
        try:
            with open(coordinators_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"course_coordinators": []}
    return {"course_coordinators": []}


def save_coordinators_data(data):
    """Save course coordinators data"""
    coordinators_file = Path(__file__).parent.parent / 'data' / 'course_coordinators.json'
    try:
        with open(coordinators_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


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


def load_faculty_data():
    """Load faculty members data"""
    faculty_file = Path(__file__).parent.parent / 'data' / 'faculty.json'
    if faculty_file.exists():
        try:
            with open(faculty_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"faculty_members": []}
    return {"faculty_members": []}


def load_external_teaching_data():
    """Load external teaching assignments data"""
    external_file = Path(__file__).parent.parent / 'data' / 'external_teaching.json'
    if external_file.exists():
        try:
            with open(external_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"external_assignments": []}
    return {"external_assignments": []}


def get_course_beneficiaries(course_id: str, external_assignments: list, programs: list) -> list:
    """Get all beneficiary colleges/departments for a course (original + external)"""
    beneficiaries = []

    # Get external beneficiaries for this course
    for assignment in external_assignments:
        if assignment.get('course_id') == course_id and assignment.get('is_active', True):
            beneficiaries.append({
                'type': 'external',
                'college_ar': assignment.get('target_college_ar', ''),
                'college_en': assignment.get('target_college_en', ''),
                'department_ar': assignment.get('target_department_ar', ''),
                'department_en': assignment.get('target_department_en', ''),
                'display': f"🏫 {assignment.get('target_college_en', '')} / {assignment.get('target_department_en', '')}"
            })

    return beneficiaries


def generate_semester_code(academic_year: str, semester_type: str) -> str:
    """
    Generate semester code based on academic year and semester type
    Format: Last 2 digits of year + semester number (1=First, 2=Second, 5=Summer)
    Example: 1447 First semester = 471
    """
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


def get_courses_by_program(program_id: str, courses: list) -> list:
    """Get courses filtered by program"""
    return [c for c in courses if c.get('program_id') == program_id]


def get_coordinator_for_course_semester(coordinators: list, course_id: str, semester_code: str) -> dict:
    """Get coordinator for a specific course and semester"""
    for coord in coordinators:
        if coord.get('course_id') == course_id and coord.get('semester_code') == semester_code:
            return coord
    return None


def show_sections_management(db: Database, user, lang: str):
    """Display Sections Management page"""

    # Check if user is section instructor (view-only mode)
    is_section_instructor = user.role == UserRole.SECTION_INSTRUCTOR

    # Initialize permissions helper
    perm = get_permissions_helper(db, user)

    # Load data and apply permissions filtering
    sections_data = load_sections_data()
    all_sections = sections_data.get('sections', [])
    sections = perm.filter_sections(all_sections)

    courses_data = load_courses_data()
    all_courses = courses_data.get('courses', [])
    courses = perm.filter_courses(all_courses)

    # ═══════════════════════════════════════════════════════════════
    # SECTION INSTRUCTOR VIEW - Simple read-only view
    # ═══════════════════════════════════════════════════════════════
    if is_section_instructor:
        st.title("My Sections / شعبي")
        st.caption("View your assigned sections / عرض الشعب المسندة إليك")

        if not sections:
            st.info("لا توجد شعب مسندة إليك حالياً / No sections assigned to you yet")
            return

        # Display sections in a table format
        st.markdown("### Assigned Sections / الشعب المسندة")

        # Create display data
        sections_display = []
        for s in sections:
            course_info = next((c for c in all_courses if c.get('course_id') == s.get('course_id')), None)
            course_name = course_info.get('course_title_en', '') if course_info else ''

            sections_display.append({
                'Course Code / رمز المقرر': s.get('course_code', ''),
                'Course Name / اسم المقرر': course_name,
                'Section / الشعبة': s.get('section_number', ''),
                'Semester / الفصل': s.get('semester', ''),
                'Year / السنة': s.get('academic_year', ''),
                'Gender / النوع': s.get('gender', '')
            })

        import pandas as pd
        df = pd.DataFrame(sections_display)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.caption(f"Total Sections: {len(sections)} / إجمالي الشعب: {len(sections)}")

        # Info message
        st.info("💡 لإدارة طلاب الشعبة، انتقل إلى صفحة 'طلاب الشعبة' / To manage section students, go to 'Section Students' page")

        return  # Exit early for section instructors

    # ═══════════════════════════════════════════════════════════════
    # NORMAL MANAGEMENT VIEW - Full editing capabilities
    # ═══════════════════════════════════════════════════════════════
    st.title("Sections Management / ادارة الشعب")

    # Check if user is course coordinator (they cannot edit coordinator assignments)
    is_course_coordinator = user.role == UserRole.COURSE_COORDINATOR
    can_edit_coordinator = user.role in [UserRole.ADMIN, UserRole.PROGRAM_COORDINATOR]

    coordinators_data = load_coordinators_data()
    coordinators = coordinators_data.get('course_coordinators', [])

    programs_data = load_programs_data()
    all_programs = programs_data.get('programs', [])
    programs = perm.filter_programs(all_programs)

    faculty_data = load_faculty_data()
    faculty_members = faculty_data.get('faculty_members', [])

    external_data = load_external_teaching_data()
    external_assignments = external_data.get('external_assignments', [])

    # Prepare program list (filtered by permissions)
    program_list = [(p.get('program_id'), f"{p.get('program_code', '')} - {p.get('program_name_en', '')}") for p in programs if p.get('is_active', True)]

    # Academic year options (Hijri years)
    academic_years = ["1446", "1447", "1448", "1449", "1450"]

    # Semester options
    semester_options = ["First / الأول", "Second / الثاني", "Summer / صيفي"]

    # Gender options
    gender_options = ["Male / ذكور", "Female / اناث"]

    # ===========================================
    # Section 1: Course Coordinator Assignment
    # ===========================================
    st.markdown("### 1. Course Coordinator / منسق المقرر")
    st.caption("First, assign a coordinator for the course in a specific semester")

    # Show success/error messages from session state
    if st.session_state.get('coord_message'):
        msg_type, msg_text = st.session_state.coord_message
        if msg_type == 'success':
            st.success(msg_text)
        elif msg_type == 'error':
            st.error(msg_text)
        # Clear message after showing
        st.session_state.coord_message = None

    coord_col1, coord_col2, coord_col3 = st.columns(3)

    with coord_col1:
        # Program selection for coordinator
        if program_list:
            coord_program_options = ["-- Select Program --"] + [p[1] for p in program_list]

            # Check if there's a selected coordinator from list
            selected_program_index = 0
            if st.session_state.get('selected_coord_program_id'):
                for i, p in enumerate(program_list):
                    if p[0] == st.session_state.selected_coord_program_id:
                        selected_program_index = i + 1  # +1 for "-- Select Program --"
                        break

            coord_selected_program = st.selectbox("Program", coord_program_options, index=selected_program_index, key="coord_program")

            coord_program_id = None
            if coord_selected_program != "-- Select Program --":
                for p in program_list:
                    if p[1] == coord_selected_program:
                        coord_program_id = p[0]
                        break
        else:
            coord_program_id = None

        # Course selection for coordinator
        if coord_program_id:
            coord_program_courses = get_courses_by_program(coord_program_id, courses)
            if coord_program_courses:
                coord_course_options = ["-- Select Course --"] + [f"{c.get('course_code', '')} - {c.get('course_title_en', '')}" for c in coord_program_courses]

                # Check if there's a selected course from list
                selected_course_index = 0
                if st.session_state.get('selected_coord_course_id'):
                    for i, c in enumerate(coord_program_courses):
                        if c.get('course_id') == st.session_state.selected_coord_course_id:
                            selected_course_index = i + 1  # +1 for "-- Select Course --"
                            break

                coord_selected_course_display = st.selectbox("Course", coord_course_options, index=selected_course_index, key="coord_course")

                coord_selected_course = None
                if coord_selected_course_display != "-- Select Course --":
                    for c in coord_program_courses:
                        if f"{c.get('course_code', '')} - {c.get('course_title_en', '')}" == coord_selected_course_display:
                            coord_selected_course = c
                            break
            else:
                coord_selected_course = None
        else:
            coord_selected_course = None

    with coord_col2:
        # Year and Semester for coordinator
        # Check if there's a selected year from list
        selected_year_index = 0
        if st.session_state.get('selected_coord_year'):
            if st.session_state.selected_coord_year in academic_years:
                selected_year_index = academic_years.index(st.session_state.selected_coord_year) + 1

        coord_year = st.selectbox("Academic Year", ["-- Select --"] + academic_years, index=selected_year_index, key="coord_year")

        # Check if there's a selected semester from list
        selected_semester_index = 0
        if st.session_state.get('selected_coord_semester'):
            if st.session_state.selected_coord_semester in semester_options:
                selected_semester_index = semester_options.index(st.session_state.selected_coord_semester) + 1

        coord_semester = st.selectbox("Semester", ["-- Select --"] + semester_options, index=selected_semester_index, key="coord_semester")

        # Calculate semester code
        coord_semester_code = ""
        if coord_year != "-- Select --" and coord_semester != "-- Select --":
            coord_semester_code = generate_semester_code(coord_year, coord_semester)
            st.caption(f"Semester Code: **{coord_semester_code}**")

    with coord_col3:
        # Show current coordinator if exists
        current_coordinator = None
        current_coordinator_name = "Not assigned"
        existing_coord = None

        if coord_selected_course and coord_semester_code:
            existing_coord = get_coordinator_for_course_semester(
                coordinators,
                coord_selected_course.get('course_id'),
                coord_semester_code
            )
            if existing_coord:
                current_coordinator = existing_coord.get('coordinator_id')
                for fm in faculty_members:
                    if fm.get('employee_id') == current_coordinator:
                        current_coordinator_name = fm.get('name', '')
                        break

        # Display current coordinator with colored badge
        if current_coordinator:
            st.markdown(f"""
            <div style="background-color: #d4edda; padding: 8px 12px; border-radius: 5px; margin-bottom: 10px;">
                <strong>Current:</strong> {current_coordinator_name}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color: #fff3cd; padding: 8px 12px; border-radius: 5px; margin-bottom: 10px;">
                <strong>Current:</strong> Not assigned
            </div>
            """, unsafe_allow_html=True)

        # Only show editing controls for Admin and Program Coordinator
        if can_edit_coordinator:
            # Coordinator selection
            coord_faculty_options = ["-- Select Coordinator --"] + [f"{fm.get('employee_id')} - {fm.get('name')}" for fm in faculty_members]

            # Find current index
            coord_faculty_index = 0
            if current_coordinator:
                for i, opt in enumerate(coord_faculty_options):
                    if current_coordinator and opt.startswith(current_coordinator):
                        coord_faculty_index = i
                        break

            new_coordinator = st.selectbox("Assign/Change Coordinator", coord_faculty_options, index=coord_faculty_index, key="coord_faculty")

            # Action buttons
            btn_col1, btn_col2 = st.columns(2)

            with btn_col1:
                # Save coordinator button
                if st.button("Save", type="primary", key="save_coordinator_btn", use_container_width=True):
                    if not coord_selected_course:
                        st.session_state.coord_message = ('error', "Please select a course!")
                        st.rerun()
                    elif not coord_semester_code:
                        st.session_state.coord_message = ('error', "Please select year and semester!")
                        st.rerun()
                    elif new_coordinator == "-- Select Coordinator --":
                        st.session_state.coord_message = ('error', "Please select a coordinator!")
                        st.rerun()
                    else:
                        new_coord_id = new_coordinator.split(' - ')[0]
                        new_coord_name = new_coordinator.split(' - ')[1] if ' - ' in new_coordinator else new_coord_id

                        # Check if coordinator record exists
                        coord_exists = False
                        for i, coord in enumerate(coordinators_data['course_coordinators']):
                            if (coord.get('course_id') == coord_selected_course.get('course_id') and
                                coord.get('semester_code') == coord_semester_code):
                                # Update existing
                                coordinators_data['course_coordinators'][i]['coordinator_id'] = new_coord_id
                                coordinators_data['course_coordinators'][i]['updated_at'] = datetime.now().isoformat()
                                coord_exists = True
                                break

                        if not coord_exists:
                            # Create new coordinator record
                            new_coord_record = {
                                "coordinator_record_id": f"coord_{coord_selected_course.get('course_id')}_{coord_semester_code}",
                                "program_id": coord_program_id,
                                "course_id": coord_selected_course.get('course_id'),
                                "course_code": coord_selected_course.get('course_code'),
                                "academic_year": coord_year,
                                "semester": coord_semester,
                                "semester_code": coord_semester_code,
                                "coordinator_id": new_coord_id,
                                "created_at": datetime.now().isoformat()
                            }
                            coordinators_data['course_coordinators'].append(new_coord_record)

                        if save_coordinators_data(coordinators_data):
                            action = "updated" if coord_exists else "assigned"
                            st.session_state.coord_message = ('success', f"Coordinator {action} successfully: {new_coord_name}")
                            # Clear selection state
                            st.session_state.selected_coord_program_id = None
                            st.session_state.selected_coord_course_id = None
                            st.session_state.selected_coord_year = None
                            st.session_state.selected_coord_semester = None
                            st.rerun()
                        else:
                            st.session_state.coord_message = ('error', "Error saving coordinator!")
                            st.rerun()

            with btn_col2:
                # Delete coordinator button (only show if coordinator exists)
                if existing_coord:
                    if st.button("Delete", key="delete_coordinator_btn", use_container_width=True):
                        st.session_state.show_delete_coord_confirm = True
        else:
            # Course coordinator can only view
            st.info("👁️ للعرض فقط / View only")

    # Delete confirmation for coordinator (only for those who can edit)
    if can_edit_coordinator and st.session_state.get('show_delete_coord_confirm', False) and existing_coord:
        st.warning(f"Are you sure you want to remove **{current_coordinator_name}** as coordinator for **{coord_selected_course.get('course_code')}** ({coord_semester_code})?")

        del_col1, del_col2, del_col3 = st.columns([1, 1, 2])
        with del_col1:
            if st.button("Yes, Delete", type="primary", key="confirm_delete_coord"):
                # Remove coordinator
                coordinators_data['course_coordinators'] = [
                    c for c in coordinators_data['course_coordinators']
                    if not (c.get('course_id') == coord_selected_course.get('course_id') and
                           c.get('semester_code') == coord_semester_code)
                ]

                if save_coordinators_data(coordinators_data):
                    st.session_state.coord_message = ('success', f"Coordinator removed successfully!")
                    st.session_state.show_delete_coord_confirm = False
                    # Clear selection state
                    st.session_state.selected_coord_program_id = None
                    st.session_state.selected_coord_course_id = None
                    st.session_state.selected_coord_year = None
                    st.session_state.selected_coord_semester = None
                    st.rerun()
                else:
                    st.session_state.coord_message = ('error', "Error removing coordinator!")
                    st.rerun()

        with del_col2:
            if st.button("Cancel", key="cancel_delete_coord"):
                st.session_state.show_delete_coord_confirm = False
                st.rerun()

    # Show assigned coordinators list
    if coordinators:
        st.markdown("---")
        if can_edit_coordinator:
            st.markdown("**Assigned Coordinators:** (click to select)")
        else:
            st.markdown("**Assigned Coordinators:**")

        # Create a simple table header
        if can_edit_coordinator:
            coord_header = st.columns([0.4, 1.2, 1, 0.8, 1.8])
            with coord_header[0]:
                st.markdown("**#**")
        else:
            coord_header = st.columns([1.2, 1, 0.8, 1.8])
        with coord_header[0 if not can_edit_coordinator else 1]:
            st.markdown("**Course**")
        with coord_header[1 if not can_edit_coordinator else 2]:
            st.markdown("**Semester**")
        with coord_header[2 if not can_edit_coordinator else 3]:
            st.markdown("**Code**")
        with coord_header[3 if not can_edit_coordinator else 4]:
            st.markdown("**Coordinator**")

        for idx, coord in enumerate(coordinators):
            if can_edit_coordinator:
                coord_row = st.columns([0.4, 1.2, 1, 0.8, 1.8])
            else:
                coord_row = st.columns([1.2, 1, 0.8, 1.8])

            # Get coordinator name
            coord_id = coord.get('coordinator_id', '')
            coord_name = coord_id
            for fm in faculty_members:
                if fm.get('employee_id') == coord_id:
                    coord_name = fm.get('name', '')
                    break

            # Get semester display
            sem = coord.get('semester', '')
            sem_short = sem.split(' / ')[0] if ' / ' in sem else sem

            col_offset = 0 if not can_edit_coordinator else 1

            if can_edit_coordinator:
                with coord_row[0]:
                    # Select button
                    if st.button("Select", key=f"select_coord_{idx}", use_container_width=True):
                        # Store selected coordinator info in session state to load into form
                        st.session_state.selected_coord_program_id = coord.get('program_id')
                        st.session_state.selected_coord_course_id = coord.get('course_id')
                        st.session_state.selected_coord_year = coord.get('academic_year')
                        st.session_state.selected_coord_semester = coord.get('semester')
                        st.session_state.coord_message = ('success', f"Selected: {coord.get('course_code')} - {coord.get('academic_year')} {sem_short}. Now you can edit or delete.")
                        st.rerun()

            with coord_row[col_offset]:
                st.caption(coord.get('course_code', ''))
            with coord_row[col_offset + 1]:
                st.caption(f"{coord.get('academic_year', '')} {sem_short}")
            with coord_row[col_offset + 2]:
                st.caption(coord.get('semester_code', ''))
            with coord_row[col_offset + 3]:
                st.caption(coord_name)

    st.markdown("---")

    # ===========================================
    # Section 2: Sections List
    # ===========================================
    st.markdown("### 2. Sections List / قائمة الشعب")

    # Search box
    search_col1, search_col2 = st.columns([1, 4])
    with search_col1:
        st.markdown("**Search:**")
    with search_col2:
        search_term = st.text_input("Search", label_visibility="collapsed", key="sections_search")

    # Filter sections based on search
    if search_term:
        filtered_sections = [
            s for s in sections
            if search_term.lower() in s.get('course_code', '').lower()
            or search_term.lower() in s.get('section_number', '').lower()
            or search_term.lower() in s.get('semester_code', '').lower()
            or search_term.lower() in s.get('academic_year', '').lower()
        ]
    else:
        filtered_sections = sections

    if filtered_sections:
        # Create table header
        header_cols = st.columns([0.6, 1, 0.6, 0.6, 0.5, 0.6, 1.2, 1.2, 1.2])
        with header_cols[0]:
            st.markdown("**Sec #**")
        with header_cols[1]:
            st.markdown("**Course**")
        with header_cols[2]:
            st.markdown("**Year**")
        with header_cols[3]:
            st.markdown("**Sem**")
        with header_cols[4]:
            st.markdown("**Code**")
        with header_cols[5]:
            st.markdown("**Gender**")
        with header_cols[6]:
            st.markdown("**Beneficiary**")
        with header_cols[7]:
            st.markdown("**Coordinator**")
        with header_cols[8]:
            st.markdown("**Instructor**")

        st.markdown("---")

        # Initialize selected section in session state
        if 'selected_section_id' not in st.session_state:
            st.session_state.selected_section_id = None

        # Display sections
        for section in filtered_sections:
            row_cols = st.columns([0.6, 1, 0.6, 0.6, 0.5, 0.6, 1.2, 1.2, 1.2])

            with row_cols[0]:
                if st.button(str(section.get('section_number', '')), key=f"sel_{section.get('section_id')}", use_container_width=True):
                    st.session_state.selected_section_id = section.get('section_id')
                    st.rerun()
            with row_cols[1]:
                st.markdown(f"{section.get('course_code', '')}")
            with row_cols[2]:
                st.markdown(f"{section.get('academic_year', '')}")
            with row_cols[3]:
                semester = section.get('semester', '')
                sem_short = semester.split(' / ')[0] if ' / ' in semester else semester
                st.markdown(f"{sem_short}")
            with row_cols[4]:
                st.markdown(f"{section.get('semester_code', '')}")
            with row_cols[5]:
                gender = section.get('gender', '')
                gender_short = gender.split(' / ')[0] if ' / ' in gender else gender
                st.markdown(f"{gender_short}")
            with row_cols[6]:
                # Show beneficiary department
                beneficiary_type = section.get('beneficiary_type', 'original')
                if beneficiary_type == 'external':
                    beneficiary_dept = section.get('beneficiary_department_en', '')[:15]
                    if len(section.get('beneficiary_department_en', '')) > 15:
                        beneficiary_dept += ".."
                    st.markdown(f"🏫 {beneficiary_dept}")
                else:
                    st.markdown("🏠 Original")
            with row_cols[7]:
                # Get coordinator for this course/semester
                coord = get_coordinator_for_course_semester(
                    coordinators,
                    section.get('course_id'),
                    section.get('semester_code')
                )
                coord_name = "-"
                if coord:
                    coord_id = coord.get('coordinator_id')
                    for fm in faculty_members:
                        if fm.get('employee_id') == coord_id:
                            coord_name = fm.get('name', '')[:12] + ".." if len(fm.get('name', '')) > 12 else fm.get('name', '')
                            break
                st.markdown(f"{coord_name}")
            with row_cols[8]:
                instructor_id = section.get('instructor_id', '')
                instructor_name = "-"
                for fm in faculty_members:
                    if fm.get('employee_id') == instructor_id:
                        instructor_name = fm.get('name', '')[:12] + ".." if len(fm.get('name', '')) > 12 else fm.get('name', '')
                        break
                st.markdown(f"{instructor_name}")
    else:
        st.info("No sections found. Click 'Add' to add a new section.")

    st.markdown("---")

    # Action buttons
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 2])

    with btn_col1:
        add_btn = st.button("+ Add", type="primary", use_container_width=True)
    with btn_col2:
        edit_btn = st.button("Edit", use_container_width=True)
    with btn_col3:
        delete_btn = st.button("Delete", use_container_width=True)

    st.caption(f"Total Sections: {len(sections)}")

    # Add new section dialog
    if add_btn:
        st.session_state.show_add_section_dialog = True

    if st.session_state.get('show_add_section_dialog', False):
        st.subheader("Add New Section / اضافة شعبة جديدة")

        col1, col2 = st.columns(2)
        with col1:
            # Program selectbox
            if program_list:
                program_options = ["-- Select Program --"] + [p[1] for p in program_list]
                selected_program_display = st.selectbox("Program *", program_options, key="add_program")

                # Get selected program ID
                selected_program_id = None
                if selected_program_display != "-- Select Program --":
                    for p in program_list:
                        if p[1] == selected_program_display:
                            selected_program_id = p[0]
                            break
            else:
                st.warning("No active programs found. Please add programs first.")
                selected_program_id = None

            # Course selectbox (depends on selected program)
            if selected_program_id:
                program_courses = get_courses_by_program(selected_program_id, courses)
                if program_courses:
                    course_options = ["-- Select Course --"] + [f"{c.get('course_code', '')} - {c.get('course_title_en', '')}" for c in program_courses]
                    selected_course_display = st.selectbox("Course *", course_options, key="add_course")

                    # Get selected course
                    selected_course = None
                    if selected_course_display != "-- Select Course --":
                        for c in program_courses:
                            if f"{c.get('course_code', '')} - {c.get('course_title_en', '')}" == selected_course_display:
                                selected_course = c
                                break
                else:
                    st.warning("No courses found for selected program.")
                    selected_course = None
                    selected_course_display = st.text_input("Course (Select Program with courses)", disabled=True, key="add_course_disabled")
            else:
                selected_course = None
                selected_course_display = st.text_input("Course (Select Program first)", disabled=True, key="add_course_disabled2")

            # Version
            course_version = "1"
            if selected_course:
                course_version = selected_course.get('course_version', '1')
            st.text_input("Version", value=course_version, disabled=True, key="add_version")

            # Academic Year
            new_academic_year = st.selectbox("Academic Year *", ["-- Select Year --"] + academic_years, key="add_year")

        with col2:
            # Semester
            new_semester = st.selectbox("Semester *", ["-- Select Semester --"] + semester_options, key="add_semester")

            # Semester Code (auto-calculated)
            semester_code = ""
            if new_academic_year != "-- Select Year --" and new_semester != "-- Select Semester --":
                semester_code = generate_semester_code(new_academic_year, new_semester)
            st.text_input("Semester Code", value=semester_code, disabled=True, key="add_semester_code")

            # Gender
            new_gender = st.selectbox("Gender *", ["-- Select Gender --"] + gender_options, key="add_gender")

            # Section Number
            new_section_number = st.text_input("Section Number *", key="add_section_number", placeholder="e.g., 1, 2, 3 or A, B, C")

            # Instructor (optional)
            instructor_options = ["-- Select Instructor (Optional) --"] + [f"{fm.get('employee_id')} - {fm.get('name')}" for fm in faculty_members]
            selected_instructor = st.selectbox("Section Instructor", instructor_options, key="add_instructor")

        # Check if course has external teaching assignments
        selected_beneficiary = None
        beneficiary_info = None

        if selected_course:
            course_beneficiaries = get_course_beneficiaries(selected_course.get('course_id'), external_assignments, programs)

            if course_beneficiaries:
                st.markdown("---")
                st.markdown("#### 🏫 الجهة المستفيدة / Beneficiary Department")
                st.info("💡 هذا المقرر يُدرّس لجهات خارجية. اختر الجهة المستفيدة من هذه الشعبة.")
                st.caption("This course is taught to external departments. Select the beneficiary for this section.")

                # Get the source program info
                source_program = next((p for p in programs if p.get('program_id') == selected_course.get('program_id')), None)
                source_display = f"🏠 {source_program.get('college_en', 'N/A')} / {source_program.get('department_en', 'N/A')} (القسم الأصلي / Original Dept.)" if source_program else "Original Department"

                # Build beneficiary options
                beneficiary_options = [source_display] + [b.get('display') for b in course_beneficiaries]

                selected_beneficiary_display = st.selectbox(
                    "Select Beneficiary / اختر الجهة المستفيدة *",
                    beneficiary_options,
                    key="add_beneficiary"
                )

                # Determine selected beneficiary info
                if selected_beneficiary_display == source_display:
                    # Original department
                    beneficiary_info = {
                        'type': 'original',
                        'college_ar': source_program.get('college_ar', '') if source_program else '',
                        'college_en': source_program.get('college_en', '') if source_program else '',
                        'department_ar': source_program.get('department_ar', '') if source_program else '',
                        'department_en': source_program.get('department_en', '') if source_program else ''
                    }
                else:
                    # External beneficiary
                    for b in course_beneficiaries:
                        if b.get('display') == selected_beneficiary_display:
                            beneficiary_info = b
                            break

        submit_col1, submit_col2, submit_col3 = st.columns([1, 1, 2])
        with submit_col1:
            if st.button("Save", type="primary", use_container_width=True, key="add_save_btn"):
                # Validation
                if not selected_program_id:
                    st.error("Please select a program!")
                elif not selected_course:
                    st.error("Please select a course!")
                elif new_academic_year == "-- Select Year --":
                    st.error("Please select an academic year!")
                elif new_semester == "-- Select Semester --":
                    st.error("Please select a semester!")
                elif new_gender == "-- Select Gender --":
                    st.error("Please select a gender!")
                elif not new_section_number:
                    st.error("Please enter a section number!")
                else:
                    # Check for duplicate section (including beneficiary)
                    duplicate_found = False
                    check_beneficiary_dept = beneficiary_info.get('department_en', '') if beneficiary_info else ''
                    for s in sections:
                        existing_beneficiary_dept = s.get('beneficiary_department_en', '')
                        if (s.get('course_id') == selected_course.get('course_id') and
                            s.get('academic_year') == new_academic_year and
                            s.get('semester') == new_semester and
                            s.get('gender') == new_gender and
                            s.get('section_number') == new_section_number and
                            existing_beneficiary_dept == check_beneficiary_dept):
                            duplicate_found = True
                            break

                    if duplicate_found:
                        st.error("This section already exists!")
                    else:
                        # Get instructor ID
                        instructor_id = ""
                        if selected_instructor != "-- Select Instructor (Optional) --":
                            instructor_id = selected_instructor.split(' - ')[0]

                        # Create new section
                        new_section = {
                            "section_id": f"section_{selected_course.get('course_id')}_{new_section_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "program_id": selected_program_id,
                            "course_id": selected_course.get('course_id'),
                            "course_code": selected_course.get('course_code'),
                            "course_version": course_version,
                            "academic_year": new_academic_year,
                            "semester": new_semester,
                            "semester_code": semester_code,
                            "gender": new_gender,
                            "section_number": new_section_number,
                            "instructor_id": instructor_id,
                            "students": [],
                            "created_at": datetime.now().isoformat()
                        }

                        # Add beneficiary info if course has external teaching
                        if beneficiary_info:
                            new_section["beneficiary_type"] = beneficiary_info.get('type', 'original')
                            new_section["beneficiary_college_ar"] = beneficiary_info.get('college_ar', '')
                            new_section["beneficiary_college_en"] = beneficiary_info.get('college_en', '')
                            new_section["beneficiary_department_ar"] = beneficiary_info.get('department_ar', '')
                            new_section["beneficiary_department_en"] = beneficiary_info.get('department_en', '')

                        sections_data['sections'].append(new_section)
                        if save_sections_data(sections_data):
                            st.success("Section added successfully!")
                            st.session_state.show_add_section_dialog = False
                            st.rerun()
                        else:
                            st.error("Error saving data!")

        with submit_col2:
            if st.button("Cancel", use_container_width=True, key="add_cancel_btn"):
                st.session_state.show_add_section_dialog = False
                st.rerun()

        st.markdown("---")

    # Edit section dialog
    if edit_btn:
        if st.session_state.selected_section_id:
            st.session_state.show_edit_section_dialog = True
        else:
            st.warning("Please select a section to edit")

    if st.session_state.get('show_edit_section_dialog', False) and st.session_state.selected_section_id:
        selected_section = next((s for s in sections if s.get('section_id') == st.session_state.selected_section_id), None)

        if selected_section:
            st.subheader("Edit Section / تعديل الشعبة")

            col1, col2 = st.columns(2)
            with col1:
                # Display program and course (read-only for edit)
                st.text_input("Course Code", value=selected_section.get('course_code', ''), disabled=True, key="edit_course_code")
                st.text_input("Version", value=selected_section.get('course_version', '1'), disabled=True, key="edit_version")

                # Academic Year
                current_year = selected_section.get('academic_year', '')
                year_index = academic_years.index(current_year) + 1 if current_year in academic_years else 0
                edit_academic_year = st.selectbox("Academic Year *", ["-- Select Year --"] + academic_years, index=year_index, key="edit_year")

            with col2:
                # Semester
                current_semester = selected_section.get('semester', '')
                semester_index = semester_options.index(current_semester) + 1 if current_semester in semester_options else 0
                edit_semester = st.selectbox("Semester *", ["-- Select Semester --"] + semester_options, index=semester_index, key="edit_semester")

                # Semester Code (auto-calculated)
                edit_semester_code = ""
                if edit_academic_year != "-- Select Year --" and edit_semester != "-- Select Semester --":
                    edit_semester_code = generate_semester_code(edit_academic_year, edit_semester)
                st.text_input("Semester Code", value=edit_semester_code, disabled=True, key="edit_semester_code")

                # Gender
                current_gender = selected_section.get('gender', '')
                gender_index = gender_options.index(current_gender) + 1 if current_gender in gender_options else 0
                edit_gender = st.selectbox("Gender *", ["-- Select Gender --"] + gender_options, index=gender_index, key="edit_gender")

                # Section Number
                edit_section_number = st.text_input("Section Number *", value=selected_section.get('section_number', ''), key="edit_section_number")

                # Instructor
                current_instructor_id = selected_section.get('instructor_id', '')
                instructor_options = ["-- Select Instructor (Optional) --"] + [f"{fm.get('employee_id')} - {fm.get('name')}" for fm in faculty_members]
                instructor_index = 0
                for i, opt in enumerate(instructor_options):
                    if current_instructor_id and opt.startswith(current_instructor_id):
                        instructor_index = i
                        break
                edit_instructor = st.selectbox("Section Instructor", instructor_options, index=instructor_index, key="edit_instructor")

            # Show beneficiary info if exists (read-only)
            if selected_section.get('beneficiary_type') == 'external':
                st.markdown("---")
                st.markdown("#### 🏫 الجهة المستفيدة / Beneficiary Department")
                beneficiary_college = selected_section.get('beneficiary_college_en', 'N/A')
                beneficiary_dept = selected_section.get('beneficiary_department_en', 'N/A')
                st.info(f"🏫 {beneficiary_college} / {beneficiary_dept}")

            submit_col1, submit_col2, submit_col3 = st.columns([1, 1, 2])
            with submit_col1:
                if st.button("Update", type="primary", use_container_width=True, key="edit_update_btn"):
                    # Validation
                    if edit_academic_year == "-- Select Year --":
                        st.error("Please select an academic year!")
                    elif edit_semester == "-- Select Semester --":
                        st.error("Please select a semester!")
                    elif edit_gender == "-- Select Gender --":
                        st.error("Please select a gender!")
                    elif not edit_section_number:
                        st.error("Please enter a section number!")
                    else:
                        # Get instructor ID
                        instructor_id = ""
                        if edit_instructor != "-- Select Instructor (Optional) --":
                            instructor_id = edit_instructor.split(' - ')[0]

                        # Update section
                        for i, s in enumerate(sections_data['sections']):
                            if s.get('section_id') == st.session_state.selected_section_id:
                                sections_data['sections'][i].update({
                                    "academic_year": edit_academic_year,
                                    "semester": edit_semester,
                                    "semester_code": edit_semester_code,
                                    "gender": edit_gender,
                                    "section_number": edit_section_number,
                                    "instructor_id": instructor_id,
                                    "updated_at": datetime.now().isoformat()
                                })
                                break

                        if save_sections_data(sections_data):
                            st.success("Section updated successfully!")
                            st.session_state.show_edit_section_dialog = False
                            st.rerun()
                        else:
                            st.error("Error saving data!")

            with submit_col2:
                if st.button("Cancel", use_container_width=True, key="edit_cancel_btn"):
                    st.session_state.show_edit_section_dialog = False
                    st.rerun()

            st.markdown("---")

    # Delete confirmation
    if delete_btn:
        if st.session_state.selected_section_id:
            st.session_state.show_delete_section_confirm = True
        else:
            st.warning("Please select a section to delete")

    if st.session_state.get('show_delete_section_confirm', False) and st.session_state.selected_section_id:
        selected_section = next((s for s in sections if s.get('section_id') == st.session_state.selected_section_id), None)

        if selected_section:
            st.warning(f"Are you sure you want to delete section **{selected_section.get('section_number')}** of course **{selected_section.get('course_code')}**?")

            confirm_col1, confirm_col2, confirm_col3 = st.columns([1, 1, 2])
            with confirm_col1:
                if st.button("Yes, Delete", type="primary", use_container_width=True, key="delete_confirm_btn"):
                    sections_data['sections'] = [
                        s for s in sections_data['sections']
                        if s.get('section_id') != st.session_state.selected_section_id
                    ]

                    if save_sections_data(sections_data):
                        st.success("Section deleted successfully!")
                        st.session_state.selected_section_id = None
                        st.session_state.show_delete_section_confirm = False
                        st.rerun()
                    else:
                        st.error("Error deleting section!")

            with confirm_col2:
                if st.button("Cancel", use_container_width=True, key="delete_cancel_btn"):
                    st.session_state.show_delete_section_confirm = False
                    st.rerun()

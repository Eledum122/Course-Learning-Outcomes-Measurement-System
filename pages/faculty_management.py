"""
Faculty Management Page
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from models.database import Database, UserRole


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


def load_programs_data():
    """Load programs data to get colleges and departments"""
    programs_file = Path(__file__).parent.parent / 'data' / 'programs.json'
    if programs_file.exists():
        try:
            with open(programs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"programs": []}
    return {"programs": []}


def get_colleges_and_departments():
    """Extract unique colleges and their departments from programs"""
    programs_data = load_programs_data()
    programs = programs_data.get('programs', [])

    # Dictionary: college -> set of departments
    colleges_depts = {}

    for prog in programs:
        # Use English names (or Arabic if preferred)
        college_en = prog.get('college_en', '')
        college_ar = prog.get('college_ar', '')
        dept_en = prog.get('department_en', '')
        dept_ar = prog.get('department_ar', '')

        # Create combined name for display
        college = college_en if college_en else college_ar
        department = dept_en if dept_en else dept_ar

        if college:
            if college not in colleges_depts:
                colleges_depts[college] = set()
            if department:
                colleges_depts[college].add(department)

    return colleges_depts


def save_faculty_data(data):
    """Save faculty members data"""
    faculty_file = Path(__file__).parent.parent / 'data' / 'faculty.json'
    try:
        with open(faculty_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def show_faculty_management(db: Database, user, lang: str):
    """Display Faculty Management page"""

    st.title("Faculty Management")

    # Load data
    faculty_data = load_faculty_data()
    faculty_members = faculty_data.get('faculty_members', [])

    # Search box
    search_col1, search_col2 = st.columns([1, 4])
    with search_col1:
        st.markdown("**Search:**")
    with search_col2:
        search_term = st.text_input("Search", label_visibility="collapsed", key="faculty_search")

    # Filter faculty members based on search
    if search_term:
        filtered_members = [
            m for m in faculty_members
            if search_term.lower() in m.get('name', '').lower()
            or search_term.lower() in str(m.get('employee_id', '')).lower()
            or search_term.lower() in m.get('email', '').lower()
            or search_term.lower() in m.get('department', '').lower()
        ]
    else:
        filtered_members = faculty_members

    # Faculty Members List
    st.markdown("### Faculty Members List")

    if filtered_members:
        # Create table header
        header_cols = st.columns([1, 1.5, 2, 1.2, 1.2, 1.5, 1])
        with header_cols[0]:
            st.markdown("**Employee ID**")
        with header_cols[1]:
            st.markdown("**Name**")
        with header_cols[2]:
            st.markdown("**Academic Degree**")
        with header_cols[3]:
            st.markdown("**College**")
        with header_cols[4]:
            st.markdown("**Department**")
        with header_cols[5]:
            st.markdown("**Email**")
        with header_cols[6]:
            st.markdown("**Phone**")

        st.markdown("---")

        # Initialize selected member in session state
        if 'selected_faculty_id' not in st.session_state:
            st.session_state.selected_faculty_id = None

        # Display members
        for member in filtered_members:
            row_cols = st.columns([1, 1.5, 2, 1.2, 1.2, 1.5, 1])

            is_selected = st.session_state.selected_faculty_id == member.get('employee_id')
            bg_color = "#e3f2fd" if is_selected else "transparent"

            with row_cols[0]:
                if st.button(str(member.get('employee_id', '')), key=f"sel_{member.get('employee_id')}", use_container_width=True):
                    st.session_state.selected_faculty_id = member.get('employee_id')
                    st.rerun()
            with row_cols[1]:
                st.markdown(f"{member.get('name', '')}")
            with row_cols[2]:
                st.markdown(f"{member.get('academic_degree', '')}")
            with row_cols[3]:
                st.markdown(f"{member.get('college', '')}")
            with row_cols[4]:
                st.markdown(f"{member.get('department', '')}")
            with row_cols[5]:
                st.markdown(f"{member.get('email', '-')}")
            with row_cols[6]:
                st.markdown(f"{member.get('phone', '-')}")
    else:
        st.info("No faculty members found. Click 'Add' to add a new member.")

    st.markdown("---")

    # Action buttons
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 2])

    with btn_col1:
        add_btn = st.button("+ Add", type="primary", use_container_width=True)
    with btn_col2:
        edit_btn = st.button("Edit", use_container_width=True)
    with btn_col3:
        delete_btn = st.button("Delete", use_container_width=True)

    st.caption(f"Total Members: {len(faculty_members)}")

    # Get colleges and departments from programs
    colleges_depts = get_colleges_and_departments()
    college_list = sorted(list(colleges_depts.keys()))

    # Add new member dialog
    if add_btn:
        st.session_state.show_add_dialog = True

    if st.session_state.get('show_add_dialog', False):
        st.subheader("Add New Faculty Member")

        col1, col2 = st.columns(2)
        with col1:
            new_emp_id = st.text_input("Employee ID *", key="add_emp_id")
            new_name = st.text_input("Name *", key="add_name")
            new_degree = st.selectbox("Academic Degree", [
                "Professor / استاذ",
                "Associate Professor / استاذ مشارك",
                "Assistant Professor / استاذ مساعد",
                "Lecturer / محاضر",
                "Teaching Assistant / معيد"
            ], key="add_degree")

            # College selectbox
            if college_list:
                new_college = st.selectbox("College *", ["-- Select College --"] + college_list, key="add_college")
            else:
                new_college = st.text_input("College", key="add_college_text")

        with col2:
            # Department selectbox (depends on selected college)
            if college_list and new_college and new_college != "-- Select College --":
                dept_list = sorted(list(colleges_depts.get(new_college, [])))
                new_department = st.selectbox("Department *", ["-- Select Department --"] + dept_list, key="add_dept")
            else:
                new_department = st.text_input("Department (Select College first)", key="add_dept_text", disabled=True)

            new_email = st.text_input("Email", key="add_email")
            new_phone = st.text_input("Phone", key="add_phone")

        submit_col1, submit_col2, submit_col3 = st.columns([1, 1, 2])
        with submit_col1:
            if st.button("Save", type="primary", use_container_width=True, key="add_save_btn"):
                if new_emp_id and new_name:
                    # Check if employee ID already exists
                    existing_ids = [m.get('employee_id') for m in faculty_members]
                    if new_emp_id in existing_ids:
                        st.error("Employee ID already exists!")
                    else:
                        # Clean up college/department values
                        final_college = new_college if new_college and new_college != "-- Select College --" else ""
                        final_dept = new_department if new_department and new_department != "-- Select Department --" else ""

                        new_member = {
                            "employee_id": new_emp_id,
                            "name": new_name,
                            "academic_degree": new_degree,
                            "college": final_college,
                            "department": final_dept,
                            "email": new_email,
                            "phone": new_phone,
                            "created_at": datetime.now().isoformat()
                        }
                        faculty_data['faculty_members'].append(new_member)
                        if save_faculty_data(faculty_data):
                            st.success("Faculty member added successfully!")
                            st.session_state.show_add_dialog = False
                            st.rerun()
                        else:
                            st.error("Error saving data!")
                else:
                    st.error("Employee ID and Name are required!")

        with submit_col2:
            if st.button("Cancel", use_container_width=True, key="add_cancel_btn"):
                st.session_state.show_add_dialog = False
                st.rerun()

        st.markdown("---")

    # Edit member dialog
    if edit_btn:
        if st.session_state.selected_faculty_id:
            st.session_state.show_edit_dialog = True
        else:
            st.warning("Please select a member to edit")

    if st.session_state.get('show_edit_dialog', False) and st.session_state.selected_faculty_id:
        selected_member = next((m for m in faculty_members if m.get('employee_id') == st.session_state.selected_faculty_id), None)

        if selected_member:
            st.subheader("Edit Faculty Member")

            # Initialize edit values in session state if not exists
            if 'edit_college_val' not in st.session_state:
                st.session_state.edit_college_val = selected_member.get('college', '')

            col1, col2 = st.columns(2)
            with col1:
                edit_emp_id = st.text_input("Employee ID", value=selected_member.get('employee_id', ''), disabled=True, key="edit_emp_id")
                edit_name = st.text_input("Name *", value=selected_member.get('name', ''), key="edit_name")

                degree_options = [
                    "Professor / استاذ",
                    "Associate Professor / استاذ مشارك",
                    "Assistant Professor / استاذ مساعد",
                    "Lecturer / محاضر",
                    "Teaching Assistant / معيد"
                ]
                current_degree = selected_member.get('academic_degree', '')
                degree_index = degree_options.index(current_degree) if current_degree in degree_options else 0
                edit_degree = st.selectbox("Academic Degree", degree_options, index=degree_index, key="edit_degree")

                # College selectbox
                current_college = selected_member.get('college', '')
                if college_list:
                    college_options = ["-- Select College --"] + college_list
                    if current_college in college_list:
                        college_index = college_list.index(current_college) + 1
                    else:
                        college_index = 0
                    edit_college = st.selectbox("College *", college_options, index=college_index, key="edit_college")
                else:
                    edit_college = st.text_input("College", value=current_college, key="edit_college_text")

            with col2:
                # Department selectbox (depends on selected college)
                current_department = selected_member.get('department', '')
                if college_list and edit_college and edit_college != "-- Select College --":
                    dept_list = sorted(list(colleges_depts.get(edit_college, [])))
                    if dept_list:
                        dept_options = ["-- Select Department --"] + dept_list
                        if current_department in dept_list:
                            dept_index = dept_list.index(current_department) + 1
                        else:
                            dept_index = 0
                        edit_department = st.selectbox("Department *", dept_options, index=dept_index, key="edit_dept")
                    else:
                        edit_department = st.text_input("Department", value=current_department, key="edit_dept_text")
                else:
                    edit_department = st.text_input("Department (Select College first)", key="edit_dept_disabled", disabled=True)

                edit_email = st.text_input("Email", value=selected_member.get('email', ''), key="edit_email")
                edit_phone = st.text_input("Phone", value=selected_member.get('phone', ''), key="edit_phone")

            submit_col1, submit_col2, submit_col3 = st.columns([1, 1, 2])
            with submit_col1:
                if st.button("Update", type="primary", use_container_width=True, key="edit_update_btn"):
                    if edit_name:
                        # Clean up college/department values
                        final_college = edit_college if edit_college and edit_college != "-- Select College --" else ""
                        final_dept = edit_department if edit_department and edit_department != "-- Select Department --" else ""

                        # Update member
                        for i, m in enumerate(faculty_data['faculty_members']):
                            if m.get('employee_id') == st.session_state.selected_faculty_id:
                                faculty_data['faculty_members'][i].update({
                                    "name": edit_name,
                                    "academic_degree": edit_degree,
                                    "college": final_college,
                                    "department": final_dept,
                                    "email": edit_email,
                                    "phone": edit_phone,
                                    "updated_at": datetime.now().isoformat()
                                })
                                break

                        if save_faculty_data(faculty_data):
                            st.success("Faculty member updated successfully!")
                            st.session_state.show_edit_dialog = False
                            st.rerun()
                        else:
                            st.error("Error saving data!")
                    else:
                        st.error("Name is required!")

            with submit_col2:
                if st.button("Cancel", use_container_width=True, key="edit_cancel_btn"):
                    st.session_state.show_edit_dialog = False
                    st.rerun()

            st.markdown("---")

    # Delete confirmation
    if delete_btn:
        if st.session_state.selected_faculty_id:
            st.session_state.show_delete_confirm = True
        else:
            st.warning("Please select a member to delete")

    if st.session_state.get('show_delete_confirm', False) and st.session_state.selected_faculty_id:
        selected_member = next((m for m in faculty_members if m.get('employee_id') == st.session_state.selected_faculty_id), None)

        if selected_member:
            st.warning(f"Are you sure you want to delete **{selected_member.get('name')}** (ID: {selected_member.get('employee_id')})?")

            confirm_col1, confirm_col2, confirm_col3 = st.columns([1, 1, 2])
            with confirm_col1:
                if st.button("Yes, Delete", type="primary", use_container_width=True):
                    faculty_data['faculty_members'] = [
                        m for m in faculty_data['faculty_members']
                        if m.get('employee_id') != st.session_state.selected_faculty_id
                    ]

                    if save_faculty_data(faculty_data):
                        st.success("Faculty member deleted successfully!")
                        st.session_state.selected_faculty_id = None
                        st.session_state.show_delete_confirm = False
                        st.rerun()
                    else:
                        st.error("Error deleting member!")

            with confirm_col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_delete_confirm = False
                    st.rerun()

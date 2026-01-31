"""
تقرير قياس مخرجات التعلم للمقرر
Course Learning Outcomes Assessment Report
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from io import BytesIO
from models.database import Database, UserRole
from utils.permissions import get_permissions_helper

# PDF generation imports
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


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


def load_faculty_data():
    """Load faculty data"""
    faculty_file = Path(__file__).parent.parent / 'data' / 'faculty.json'
    if faculty_file.exists():
        try:
            with open(faculty_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"faculty": []}
    return {"faculty": []}


def get_instructor_name(instructor_id):
    """Get instructor name by ID"""
    if not instructor_id:
        return ""
    faculty_data = load_faculty_data()
    for member in faculty_data.get('faculty', []):
        if member.get('faculty_id') == instructor_id:
            return member.get('name_en', member.get('name_ar', ''))
    return ""


def load_clos_data():
    """Load CLOs data"""
    clos_file = Path(__file__).parent.parent / 'data' / 'clos.json'
    if clos_file.exists():
        try:
            with open(clos_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"clos": []}
    return {"clos": []}


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


def load_student_grades_data():
    """Load student grades data"""
    grades_file = Path(__file__).parent.parent / 'data' / 'student_grades.json'
    if grades_file.exists():
        try:
            with open(grades_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"student_grades": []}
    return {"student_grades": []}


def get_section_students(section_id):
    """Get students for a specific section"""
    data = load_section_students_data()
    students = [s for s in data.get('section_students', []) if s.get('section_id') == section_id]
    return sorted(students, key=lambda x: x.get('seq', 0))


def get_course_clos(course_id):
    """Get CLOs for a course"""
    clos_data = load_clos_data()
    clos = [clo for clo in clos_data.get('clos', []) if clo.get('course_id') == course_id]
    return sorted(clos, key=lambda x: x.get('clo_code', ''))


def get_course_data(course_id):
    """Get course data"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            return course
    return {}


def get_clos_activities_distribution(course_id):
    """Get CLOs distribution across activities"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            return course.get('clos_activities_distribution', {})
    return {}


def get_section_grades(section_id):
    """Get grades for a specific section"""
    data = load_student_grades_data()
    grades = {}
    for grade in data.get('student_grades', []):
        if grade.get('section_id') == section_id:
            student_id = grade.get('student_record_id')
            if student_id not in grades:
                grades[student_id] = {}
            key = f"{grade.get('activity_name')}_{grade.get('clo_code')}"
            grades[student_id][key] = grade.get('mark', 0)
    return grades


def load_clo_semester_settings():
    """Load CLO semester settings"""
    settings_file = Path(__file__).parent.parent / 'data' / 'clo_semester_settings.json'
    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"clo_semester_settings": []}
    return {"clo_semester_settings": []}


def get_clo_settings(course_id, semester_code, clo_id, clo_defaults=None):
    """Get CLO settings for a specific semester

    First checks semester-specific settings, then falls back to CLO default values.

    Args:
        course_id: The course ID
        semester_code: The semester code (e.g., '471')
        clo_id: The CLO ID
        clo_defaults: Optional dict with default values from the CLO itself
    """
    settings_data = load_clo_semester_settings()
    settings = settings_data.get('clo_semester_settings', [])

    # First, try to find semester-specific settings
    for setting in settings:
        if (setting.get('course_id') == course_id and
            setting.get('semester_code') == semester_code and
            setting.get('clo_id') == clo_id):
            return {
                'target_percentage': setting.get('target_percentage', 70),
                'criterion_percentage': setting.get('criterion_percentage', 70)
            }

    # Fall back to CLO default values if provided
    if clo_defaults:
        return {
            'target_percentage': clo_defaults.get('target_percentage', 70),
            'criterion_percentage': clo_defaults.get('criterion_percentage', 70)
        }

    # Ultimate fallback
    return {'target_percentage': 70, 'criterion_percentage': 70}


def calculate_clo_max_marks(clos_distribution):
    """Calculate total max marks for each CLO across all activities"""
    clo_totals = {}
    for activity_name, clo_marks in clos_distribution.items():
        for clo_code, mark in clo_marks.items():
            if mark > 0:
                if clo_code not in clo_totals:
                    clo_totals[clo_code] = 0
                clo_totals[clo_code] += mark
    return clo_totals


def calculate_student_clo_achievement(student_id, clo_code, grades, clos_distribution):
    """
    Calculate a student's achievement percentage for a specific CLO
    Returns: (achieved_marks, max_marks, percentage)
    """
    achieved = 0
    max_marks = 0

    for activity_name, clo_marks in clos_distribution.items():
        if clo_code in clo_marks and clo_marks[clo_code] > 0:
            key = f"{activity_name}_{clo_code}"
            achieved += grades.get(student_id, {}).get(key, 0)
            max_marks += clo_marks[clo_code]

    if max_marks > 0:
        percentage = (achieved / max_marks) * 100
    else:
        percentage = 0

    return achieved, max_marks, percentage


def calculate_clo_actual_level(section_students, grades, clo_code, clos_distribution, criterion_percentage):
    """
    Calculate the Actual Level for a CLO

    Method:
    1. Calculate each student's achievement percentage for the CLO
    2. Count students who achieved >= criterion_percentage
    3. Actual Level = (students who achieved / total regular students) * 100

    Returns: (actual_level, students_achieved, total_students, student_details)
    """
    regular_students = [s for s in section_students if s.get('status') == 'Regular']
    total_students = len(regular_students)

    if total_students == 0:
        return 0, 0, 0, []

    students_achieved = 0
    student_details = []

    for student in regular_students:
        student_id = student.get('student_record_id')
        achieved, max_marks, percentage = calculate_student_clo_achievement(
            student_id, clo_code, grades, clos_distribution
        )

        student_details.append({
            'student_no': student.get('student_no'),
            'student_name': student.get('student_name'),
            'achieved': achieved,
            'max_marks': max_marks,
            'percentage': percentage,
            'passed': percentage >= criterion_percentage
        })

        if percentage >= criterion_percentage:
            students_achieved += 1

    actual_level = (students_achieved / total_students) * 100

    return actual_level, students_achieved, total_students, student_details


def get_assessment_result(actual_level, target_level):
    """Determine if CLO is achieved based on actual vs target level"""
    if actual_level >= target_level:
        return "Target Achieved", "#28a745"  # Green
    else:
        return "Target not Achieved", "#dc3545"  # Red


def generate_pdf_report(course_data, section_data, report_data, instructor_name, beneficiary_text, regular_students_count, summary_stats):
    """Generate a styled PDF report"""
    if not PDF_AVAILABLE:
        return None

    buffer = BytesIO()

    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    # Create styles
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='ReportTitle',
        fontSize=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1565c0'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='ReportSubtitle',
        fontSize=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#333333'),
        spaceAfter=5,
        fontName='Helvetica'
    ))

    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontSize=12,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#1565c0'),
        spaceBefore=15,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='TableCell',
        fontSize=9,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))

    styles.add(ParagraphStyle(
        name='TableCellLeft',
        fontSize=9,
        alignment=TA_LEFT,
        fontName='Helvetica'
    ))

    story = []

    # Title
    story.append(Paragraph("Course Learning Outcomes Assessment Results", styles['ReportTitle']))
    story.append(Spacer(1, 0.3*cm))

    # Course info header
    header_data = [
        ["Course:", f"{course_data.get('course_code', '')} - {course_data.get('course_title_en', '')}"],
        ["Section:", section_data.get('section_number', '')],
        ["Semester:", f"{section_data.get('semester_code', '')} {section_data.get('academic_year', '')}"],
        ["Students:", str(regular_students_count)],
    ]

    if instructor_name:
        header_data.append(["Instructor:", instructor_name])

    if beneficiary_text:
        header_data.append(["Beneficiary:", beneficiary_text])

    header_table = Table(header_data, colWidths=[3*cm, 14*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BBDEFB')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.5*cm))

    # CLO Results section
    story.append(Paragraph("Assessment Results", styles['SectionHeader']))

    # CLO Results table header
    clo_header = [
        Paragraph("<b>CLO</b>", styles['TableCell']),
        Paragraph("<b>Description</b>", styles['TableCellLeft']),
        Paragraph("<b>Criterion</b>", styles['TableCell']),
        Paragraph("<b>Target</b>", styles['TableCell']),
        Paragraph("<b>Actual</b>", styles['TableCell']),
        Paragraph("<b>Result</b>", styles['TableCell']),
    ]

    clo_data = [clo_header]

    for row in report_data:
        result_text = row.get('Result', '')
        clo_row = [
            Paragraph(row.get('CLO Code', ''), styles['TableCell']),
            Paragraph(row.get('Description', '')[:60] + ('...' if len(row.get('Description', '')) > 60 else ''), styles['TableCellLeft']),
            Paragraph(row.get('Criterion', ''), styles['TableCell']),
            Paragraph(row.get('Target', ''), styles['TableCell']),
            Paragraph(row.get('Actual', ''), styles['TableCell']),
            Paragraph(result_text, styles['TableCell']),
        ]
        clo_data.append(clo_row)

    clo_table = Table(clo_data, colWidths=[1.5*cm, 7*cm, 2*cm, 2*cm, 2*cm, 2.5*cm])

    # Build table style with row coloring
    table_style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BBDEFB')),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]

    # Color result cells based on achievement
    for i, row in enumerate(report_data, start=1):
        if row.get('Result') == 'Target Achieved':
            table_style_commands.append(('BACKGROUND', (5, i), (5, i), colors.HexColor('#C8E6C9')))
            table_style_commands.append(('TEXTCOLOR', (5, i), (5, i), colors.HexColor('#2E7D32')))
        else:
            table_style_commands.append(('BACKGROUND', (5, i), (5, i), colors.HexColor('#FFCDD2')))
            table_style_commands.append(('TEXTCOLOR', (5, i), (5, i), colors.HexColor('#C62828')))

    clo_table.setStyle(TableStyle(table_style_commands))
    story.append(clo_table)
    story.append(Spacer(1, 0.5*cm))

    # Summary section
    story.append(Paragraph("Summary", styles['SectionHeader']))

    summary_data = [
        ["Total CLOs", "Achieved", "Not Achieved", "Achievement Rate"],
        [
            str(summary_stats['total']),
            str(summary_stats['achieved']),
            str(summary_stats['not_achieved']),
            f"{summary_stats['rate']:.1f}%"
        ]
    ]

    summary_table = Table(summary_data, colWidths=[4.25*cm, 4.25*cm, 4.25*cm, 4.25*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BBDEFB')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5*cm))

    # Overall assessment
    if summary_stats['rate'] >= 70:
        assessment_text = f"Overall Assessment: The course learning outcomes are generally achieved ({summary_stats['rate']:.1f}%)"
        assessment_color = colors.HexColor('#2E7D32')
    elif summary_stats['rate'] >= 50:
        assessment_text = f"Overall Assessment: Partial achievement of course learning outcomes ({summary_stats['rate']:.1f}%)"
        assessment_color = colors.HexColor('#F57C00')
    else:
        assessment_text = f"Overall Assessment: Course learning outcomes need improvement ({summary_stats['rate']:.1f}%)"
        assessment_color = colors.HexColor('#C62828')

    assessment_style = ParagraphStyle(
        name='Assessment',
        fontSize=11,
        alignment=TA_CENTER,
        textColor=assessment_color,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph(assessment_text, assessment_style))
    story.append(Spacer(1, 0.5*cm))

    # Report date
    date_style = ParagraphStyle(
        name='DateStyle',
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#666666'),
        fontName='Helvetica'
    )
    story.append(Paragraph(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", date_style))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def show_clo_assessment_report(db: Database, user, lang: str):
    """Display CLO Assessment Report page"""

    st.title("CLO Assessment Report / تقرير قياس المخرجات")
    st.caption("Course Learning Outcomes Assessment Results")

    # Initialize permissions helper
    perm = get_permissions_helper(db, user)

    # Load sections and apply permissions filtering
    sections_data = load_sections_data()
    all_sections = sections_data.get('sections', [])
    sections = perm.filter_sections(all_sections)

    if not sections:
        st.warning("No sections assigned to you. Please contact your administrator.")
        return

    # ===============================
    # Section 1: Select Section (with filters)
    # ===============================
    st.markdown("### 1. Select Section / اختر الشعبة")

    # Load additional data for filters and apply permissions
    programs_data = load_programs_data()
    all_programs = programs_data.get('programs', [])
    programs = perm.filter_programs(all_programs)

    courses_data = load_courses_data()
    all_courses = courses_data.get('courses', [])
    courses = perm.filter_courses(all_courses)

    # Row 1: Program and Course
    col1, col2 = st.columns(2)

    with col1:
        # Program filter
        program_options = ["-- Select Program / اختر البرنامج --"]
        program_map = {}
        for p in programs:
            if p.get('is_active', True):
                display = f"{p.get('program_code', '')} - {p.get('program_name_en', '')}"
                program_options.append(display)
                program_map[display] = p.get('program_id')

        selected_program_display = st.selectbox(
            "Program / البرنامج *",
            program_options,
            key="report_program_filter"
        )

        selected_program_id = None
        if selected_program_display != "-- Select Program / اختر البرنامج --":
            selected_program_id = program_map.get(selected_program_display)

    with col2:
        # Course filter (depends on program)
        if selected_program_id:
            program_courses = [c for c in courses if c.get('program_id') == selected_program_id]
            course_options = ["-- Select Course / اختر المقرر --"]
            course_map = {}
            for c in program_courses:
                display = f"{c.get('course_code', '')} - {c.get('course_title_en', '')}"
                course_options.append(display)
                course_map[display] = c.get('course_id')

            selected_course_display = st.selectbox(
                "Course / المقرر *",
                course_options,
                key="report_course_filter"
            )

            selected_course_id = None
            if selected_course_display != "-- Select Course / اختر المقرر --":
                selected_course_id = course_map.get(selected_course_display)
        else:
            st.selectbox(
                "Course / المقرر *",
                ["-- Select Program First / اختر البرنامج أولاً --"],
                disabled=True,
                key="report_course_filter_disabled"
            )
            selected_course_id = None

    # Row 2: Academic Year and Semester
    col3, col4 = st.columns(2)

    with col3:
        # Academic Year filter
        if selected_course_id:
            # Get available years for this course
            course_sections = [s for s in sections if s.get('course_id') == selected_course_id]
            available_years = sorted(list(set(s.get('academic_year', '') for s in course_sections if s.get('academic_year'))), reverse=True)

            year_options = ["-- Select Year / اختر السنة --"] + available_years
            selected_year = st.selectbox(
                "Academic Year / السنة الدراسية *",
                year_options,
                key="report_year_filter"
            )
            if selected_year == "-- Select Year / اختر السنة --":
                selected_year = None
        else:
            st.selectbox(
                "Academic Year / السنة الدراسية *",
                ["-- Select Course First / اختر المقرر أولاً --"],
                disabled=True,
                key="report_year_filter_disabled"
            )
            selected_year = None

    with col4:
        # Semester filter
        if selected_year and selected_course_id:
            # Get available semesters for this course and year
            year_sections = [s for s in sections if s.get('course_id') == selected_course_id and s.get('academic_year') == selected_year]
            available_semesters = list(set(s.get('semester', '') for s in year_sections if s.get('semester')))

            semester_display_options = ["-- Select Semester / اختر الفصل --"] + available_semesters
            selected_semester = st.selectbox(
                "Semester / الفصل الدراسي *",
                semester_display_options,
                key="report_semester_filter"
            )
            if selected_semester == "-- Select Semester / اختر الفصل --":
                selected_semester = None
        else:
            st.selectbox(
                "Semester / الفصل الدراسي *",
                ["-- Select Year First / اختر السنة أولاً --"],
                disabled=True,
                key="report_semester_filter_disabled"
            )
            selected_semester = None

    # Row 3: Section selection
    st.markdown("---")

    if selected_course_id and selected_year and selected_semester:
        # Filter sections based on all criteria
        filtered_sections = [
            s for s in sections
            if s.get('course_id') == selected_course_id
            and s.get('academic_year') == selected_year
            and s.get('semester') == selected_semester
        ]

        if filtered_sections:
            section_options = ["-- Select Section / اختر الشعبة --"]
            section_map = {}

            for s in filtered_sections:
                section_num = s.get('section_number', '')
                gender = s.get('gender', '').split(' / ')[0] if ' / ' in s.get('gender', '') else s.get('gender', '')
                beneficiary = ""
                if s.get('beneficiary_type') == 'external':
                    beneficiary = f" - 🏫 {s.get('beneficiary_department_en', '')[:20]}"

                option_text = f"Section {section_num} - {gender}{beneficiary}"
                section_options.append(option_text)
                section_map[option_text] = s

            col5, col6 = st.columns(2)

            with col5:
                selected_section_display = st.selectbox(
                    "Section / الشعبة *",
                    section_options,
                    key="report_section_select"
                )

                selected_section = None
                if selected_section_display != "-- Select Section / اختر الشعبة --":
                    selected_section = section_map.get(selected_section_display)

            with col6:
                if selected_section:
                    beneficiary_info = ""
                    if selected_section.get('beneficiary_type') == 'external':
                        beneficiary_info = f"\n**Beneficiary:** 🏫 {selected_section.get('beneficiary_college_en', '')} / {selected_section.get('beneficiary_department_en', '')}"

                    st.success(f"""
                    **Course:** {selected_section.get('course_code')}
                    **Section:** {selected_section.get('section_number')}
                    **Semester:** {selected_section.get('academic_year')} - {selected_section.get('semester_code')}{beneficiary_info}
                    """)
        else:
            st.warning("No sections found for the selected criteria. Please check your selection.")
            selected_section = None
    else:
        st.info("💡 Please select Program, Course, Academic Year, and Semester to filter sections")
        selected_section = None

    if not selected_section:
        return

    section_id = selected_section.get('section_id')
    course_id = selected_section.get('course_id')

    # Get data
    section_students = get_section_students(section_id)
    course_clos = get_course_clos(course_id)
    course_data = get_course_data(course_id)
    clos_distribution = get_clos_activities_distribution(course_id)
    grades = get_section_grades(section_id)

    # Validate data
    if not section_students:
        st.warning("No students in this section.")
        return

    if not course_clos:
        st.warning("No CLOs defined for this course.")
        return

    if not clos_distribution:
        st.warning("CLOs distribution not defined. Please complete Stage 2.4 first.")
        return

    if not grades:
        st.warning("No grades entered for this section. Please enter grades first.")
        return

    # Count regular students
    regular_students = [s for s in section_students if s.get('status') == 'Regular']

    # Get instructor name
    instructor_name = get_instructor_name(selected_section.get('instructor_id'))

    # Get beneficiary info
    beneficiary_text = ""
    if selected_section.get('beneficiary_type') == 'external':
        beneficiary_college = selected_section.get('beneficiary_college_en', selected_section.get('beneficiary_college_ar', ''))
        beneficiary_dept = selected_section.get('beneficiary_department_en', selected_section.get('beneficiary_department_ar', ''))
        beneficiary_text = f"Beneficiary: {beneficiary_college} - {beneficiary_dept}"

    # Instructor text
    instructor_text = ""
    if instructor_name:
        instructor_text = f"Instructor: {instructor_name}"

    st.markdown("---")

    # ===============================
    # Section 2: Report Header
    # ===============================
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
                padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center;">
        <h2 style="color: white; margin: 0;">Course Learning Outcomes Assessment Results</h2>
        <h3 style="color: white; margin: 10px 0;">تقرير قياس مخرجات التعلم للمقرر</h3>
        <p style="color: #bbdefb; margin: 5px 0;">
            {course_data.get('course_code', '')} - {course_data.get('course_title_en', '')}
        </p>
        <p style="color: #bbdefb; margin: 5px 0;">
            Section: {selected_section.get('section_number')} |
            Semester: {selected_section.get('semester_code')} {selected_section.get('academic_year')} |
            Students: {len(regular_students)}
        </p>
        <p style="color: #c8e6c9; margin: 5px 0;">{instructor_text}</p>
        <p style="color: #ffeb3b; margin: 5px 0; font-weight: bold;">{beneficiary_text}</p>
    </div>
    """, unsafe_allow_html=True)

    # ===============================
    # Section 3: CLO Assessment Table
    # ===============================
    st.markdown("### 2. Assessment Results / نتائج التقييم")

    # Group CLOs by domain
    knowledge_clos = [c for c in course_clos if c.get('clo_code', '').startswith('K')]
    skills_clos = [c for c in course_clos if c.get('clo_code', '').startswith('S')]
    values_clos = [c for c in course_clos if c.get('clo_code', '').startswith('V')]

    # Calculate CLO max marks
    clo_max_marks = calculate_clo_max_marks(clos_distribution)

    # Get semester code for settings lookup
    semester_code = selected_section.get('semester_code', '')

    # Build report data
    report_data = []

    def process_clo_group(clos, domain_name, domain_color):
        """Process a group of CLOs and add to report"""
        if not clos:
            return

        # Domain header
        st.markdown(f"""
        <div style="background:{domain_color};padding:10px;border-radius:5px;margin:15px 0 10px 0;">
            <h4 style="color:white;margin:0;text-align:center;">{domain_name}</h4>
        </div>
        """, unsafe_allow_html=True)

        for clo in clos:
            clo_code = clo.get('clo_code', '')
            clo_id = clo.get('clo_id', '')
            # Use correct field names: description_en and description_ar
            clo_description = clo.get('description_en', clo.get('description_ar', ''))

            # Skip if CLO not in distribution
            if clo_code not in clo_max_marks:
                continue

            # Get CLO settings for this semester (criterion and target)
            # Pass CLO defaults as fallback if no semester-specific settings exist
            clo_defaults = {
                'criterion_percentage': clo.get('criterion_percentage', 70),
                'target_percentage': clo.get('target_percentage', 70)
            }
            clo_settings = get_clo_settings(course_id, semester_code, clo_id, clo_defaults)
            criterion_percentage = clo_settings['criterion_percentage']
            target_level = clo_settings['target_percentage']

            # Calculate actual level
            actual_level, students_achieved, total_students, student_details = calculate_clo_actual_level(
                section_students, grades, clo_code, clos_distribution, criterion_percentage
            )

            # Get assessment result
            result_text, result_color = get_assessment_result(actual_level, target_level)

            # Add to report data
            report_data.append({
                'CLO Code': clo_code,
                'Description': clo_description,
                'Criterion': f"{criterion_percentage:.0f}%",
                'Target': f"{target_level:.0f}%",
                'Actual': f"{actual_level:.1f}%",
                'Result': result_text,
                'Details': f"{students_achieved}/{total_students} students"
            })

            # Display CLO row
            col1, col2, col3, col4, col5, col6 = st.columns([3, 0.8, 0.8, 0.8, 0.8, 1.2])

            with col1:
                # Truncate description if too long
                desc_short = clo_description[:80] + "..." if len(clo_description) > 80 else clo_description
                st.markdown(f"""
                <div style="background:#f8f9fa;padding:10px;border-radius:5px;min-height:60px;">
                    <strong>{clo.get('clo_number', '')}</strong> {desc_short}
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="background:#e3f2fd;padding:10px;border-radius:5px;text-align:center;min-height:60px;">
                    <strong>{clo_code}</strong>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div style="background:#fff3e0;padding:10px;border-radius:5px;text-align:center;min-height:60px;">
                    <strong>{criterion_percentage:.0f}%</strong>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div style="background:#fff3e0;padding:10px;border-radius:5px;text-align:center;min-height:60px;">
                    <strong>{target_level:.0f}%</strong>
                </div>
                """, unsafe_allow_html=True)

            with col5:
                st.markdown(f"""
                <div style="background:#e8f5e9;padding:10px;border-radius:5px;text-align:center;min-height:60px;">
                    <strong>{actual_level:.1f}%</strong>
                </div>
                """, unsafe_allow_html=True)

            with col6:
                st.markdown(f"""
                <div style="background:{result_color};padding:10px;border-radius:5px;text-align:center;min-height:60px;">
                    <strong style="color:white;">{result_text}</strong>
                </div>
                """, unsafe_allow_html=True)

    # Table header
    header_cols = st.columns([3, 0.8, 0.8, 0.8, 0.8, 1.2])
    headers = ["Course Learning Outcomes", "PLOs Code", "Criterion for Success", "Target Level", "Actual Level", "Assessment Results"]

    for i, header in enumerate(headers):
        with header_cols[i]:
            st.markdown(f"""
            <div style="background:#1565c0;padding:10px;border-radius:5px;text-align:center;">
                <strong style="color:white;font-size:12px;">{header}</strong>
            </div>
            """, unsafe_allow_html=True)

    # Process each domain
    process_clo_group(knowledge_clos, "1 Knowledge and Understanding", "#2196f3")
    process_clo_group(skills_clos, "2 Skills", "#4caf50")
    process_clo_group(values_clos, "3 Values", "#ff9800")

    st.markdown("---")

    # ===============================
    # Section 4: Summary Statistics
    # ===============================
    st.markdown("### 3. Summary / ملخص")

    if report_data:
        achieved_count = sum(1 for r in report_data if r['Result'] == 'Target Achieved')
        total_clos = len(report_data)
        achievement_rate = (achieved_count / total_clos * 100) if total_clos > 0 else 0

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total CLOs / إجمالي المخرجات", total_clos)

        with col2:
            st.metric("Achieved / المحققة", achieved_count)

        with col3:
            st.metric("Not Achieved / غير المحققة", total_clos - achieved_count)

        with col4:
            st.metric("Achievement Rate / نسبة التحقيق", f"{achievement_rate:.1f}%")

        # Overall assessment
        if achievement_rate >= 70:
            st.success(f"Overall Assessment: The course learning outcomes are generally achieved ({achievement_rate:.1f}%)")
        elif achievement_rate >= 50:
            st.warning(f"Overall Assessment: Partial achievement of course learning outcomes ({achievement_rate:.1f}%)")
        else:
            st.error(f"Overall Assessment: Course learning outcomes need improvement ({achievement_rate:.1f}%)")

    st.markdown("---")

    # ===============================
    # Section 5: Export Options
    # ===============================
    st.markdown("### 4. Export / تصدير")

    col1, col2, col3 = st.columns(3)

    with col1:
        if report_data:
            # Create DataFrame for export
            df_export = pd.DataFrame(report_data)

            # Convert to Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='CLO Assessment')
            output.seek(0)

            st.download_button(
                label="📊 Download Excel",
                data=output,
                file_name=f"CLO_Assessment_{course_data.get('course_code', '')}_{selected_section.get('section_number')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    with col2:
        if report_data and PDF_AVAILABLE:
            # Prepare summary stats
            summary_stats = {
                'total': total_clos,
                'achieved': achieved_count,
                'not_achieved': total_clos - achieved_count,
                'rate': achievement_rate
            }

            # Generate PDF
            pdf_buffer = generate_pdf_report(
                course_data,
                selected_section,
                report_data,
                instructor_text.replace("Instructor: ", "") if instructor_text else "",
                beneficiary_text.replace("Beneficiary: ", "") if beneficiary_text else "",
                len(regular_students),
                summary_stats
            )

            if pdf_buffer:
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_buffer,
                    file_name=f"CLO_Assessment_{course_data.get('course_code', '')}_{selected_section.get('section_number')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )

    with col3:
        st.info("Report generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M"))

"""
تقرير قياس مخرجات التعلم المجمع
Collected CLO Assessment Report
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
    from reportlab.lib.units import cm, inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
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
            return {"faculty_members": []}
    return {"faculty_members": []}


def get_instructor_name(instructor_id):
    """Get instructor name by ID"""
    if not instructor_id:
        return ""
    faculty_data = load_faculty_data()
    # Check faculty_members (new format)
    for member in faculty_data.get('faculty_members', []):
        if member.get('employee_id') == instructor_id:
            return member.get('name', '')
    # Fallback to faculty (old format)
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
    """Get CLO settings for a specific semester"""
    settings_data = load_clo_semester_settings()
    settings = settings_data.get('clo_semester_settings', [])

    for setting in settings:
        if (setting.get('course_id') == course_id and
            setting.get('semester_code') == semester_code and
            setting.get('clo_id') == clo_id):
            return {
                'target_percentage': setting.get('target_percentage', 70),
                'criterion_percentage': setting.get('criterion_percentage', 70)
            }

    if clo_defaults:
        return {
            'target_percentage': clo_defaults.get('target_percentage', 70),
            'criterion_percentage': clo_defaults.get('criterion_percentage', 70)
        }

    return {'target_percentage': 70, 'criterion_percentage': 70}


def calculate_student_clo_achievement(student_id, clo_code, grades, clos_distribution):
    """Calculate a student's achievement percentage for a specific CLO"""
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
    """Calculate the Actual Level for a CLO"""
    regular_students = [s for s in section_students if s.get('status') == 'Regular']
    total_students = len(regular_students)

    if total_students == 0:
        return 0, 0, 0

    students_achieved = 0

    for student in regular_students:
        student_id = student.get('student_record_id')
        achieved, max_marks, percentage = calculate_student_clo_achievement(
            student_id, clo_code, grades, clos_distribution
        )

        if percentage >= criterion_percentage:
            students_achieved += 1

    actual_level = (students_achieved / total_students) * 100

    return actual_level, students_achieved, total_students


def get_assessment_result(actual_level, target_level):
    """Determine if CLO is achieved based on actual vs target level"""
    if actual_level >= target_level:
        return "Achieved", "#28a745"
    else:
        return "Not Achieved", "#dc3545"


def calculate_section_clo_report(section, course_data, clos, clos_distribution):
    """Calculate CLO report data for a single section"""
    section_id = section.get('section_id')
    course_id = section.get('course_id')
    semester_code = section.get('semester_code', '')

    section_students = get_section_students(section_id)
    grades = get_section_grades(section_id)

    regular_students = [s for s in section_students if s.get('status') == 'Regular']
    regular_count = len(regular_students)

    if regular_count == 0:
        return None

    report_data = []

    for clo in clos:
        clo_code = clo.get('clo_code', '')
        clo_id = clo.get('clo_id')

        # Get settings
        clo_defaults = {
            'target_percentage': clo.get('target_percentage', 70),
            'criterion_percentage': clo.get('criterion_percentage', 70)
        }
        settings = get_clo_settings(course_id, semester_code, clo_id, clo_defaults)
        target = settings['target_percentage']
        criterion = settings['criterion_percentage']

        # Calculate actual level
        actual_level, students_achieved, total_students = calculate_clo_actual_level(
            section_students, grades, clo_code, clos_distribution, criterion
        )

        # Get result
        result_text, result_color = get_assessment_result(actual_level, target)

        report_data.append({
            'clo_code': clo_code,
            'clo_description': clo.get('clo_description_en', ''),
            'target': target,
            'criterion': criterion,
            'actual_level': actual_level,
            'students_achieved': students_achieved,
            'total_students': total_students,
            'result': result_text,
            'result_color': result_color
        })

    return {
        'section': section,
        'regular_count': regular_count,
        'report_data': report_data
    }


def calculate_aggregated_results(sections_reports, clos):
    """Calculate weighted average for all CLOs across sections"""
    aggregated = []

    for clo in clos:
        clo_code = clo.get('clo_code', '')

        total_weighted = 0
        total_students = 0
        target = 70
        criterion = 70

        for section_report in sections_reports:
            if section_report is None:
                continue

            regular_count = section_report['regular_count']

            for clo_data in section_report['report_data']:
                if clo_data['clo_code'] == clo_code:
                    total_weighted += regular_count * clo_data['actual_level']
                    total_students += regular_count
                    target = clo_data['target']
                    criterion = clo_data['criterion']
                    break

        if total_students > 0:
            weighted_avg = total_weighted / total_students
        else:
            weighted_avg = 0

        result_text, result_color = get_assessment_result(weighted_avg, target)

        aggregated.append({
            'clo_code': clo_code,
            'clo_description': clo.get('clo_description_en', ''),
            'target': target,
            'criterion': criterion,
            'actual_level': weighted_avg,
            'total_students': total_students,
            'result': result_text,
            'result_color': result_color
        })

    return aggregated


def generate_aggregated_pdf_report(course_data, selected_sections, sections_reports, aggregated_results, clos, program_data=None):
    """Generate PDF report for aggregated CLO assessment"""
    if not PDF_AVAILABLE:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1*cm, leftMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=18, spaceAfter=10, textColor=colors.HexColor('#1565c0'))
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, spaceAfter=5, textColor=colors.HexColor('#666666'))
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=12, spaceAfter=8, spaceBefore=15, textColor=colors.HexColor('#333333'))
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=9)
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=8)

    elements = []

    # ===== TITLE =====
    elements.append(Paragraph("Collected CLO Assessment Report", title_style))
    elements.append(Paragraph("Consolidated Course Learning Outcomes Measurement", subtitle_style))
    elements.append(Spacer(1, 0.3*inch))

    # ===== COURSE & PROGRAM INFO =====
    total_students = sum(sr['regular_count'] for sr in sections_reports if sr)
    valid_sections_count = len([sr for sr in sections_reports if sr])

    info_data = [
        ['Course Code', course_data.get('course_code', '')],
        ['Course Title', course_data.get('course_title_en', '')],
        ['Program', program_data.get('program_name_en', 'N/A') if program_data else 'N/A'],
        ['Total Sections', str(valid_sections_count)],
        ['Total Students', str(total_students)],
        ['Total CLOs', str(len(clos))],
        ['Report Date', datetime.now().strftime('%Y-%m-%d %H:%M')],
    ]
    info_table = Table(info_data, colWidths=[4*cm, 14*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f8f9fa')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#667eea')),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#cccccc')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))

    # ===== SECTIONS SUMMARY =====
    elements.append(Paragraph("Sections Overview", section_style))

    sections_header = ['Section', 'Semester', 'Gender', 'Instructor', 'Students', 'CLOs Achieved', 'Beneficiary']
    sections_data = [sections_header]

    for i, section in enumerate(selected_sections):
        section_report = sections_reports[i]
        if section_report is None:
            continue

        instructor_name = get_instructor_name(section.get('instructor_id'))
        gender = section.get('gender', '').split(' / ')[0] if ' / ' in section.get('gender', '') else section.get('gender', '')

        # Beneficiary info
        beneficiary_info = "Internal"
        if section.get('beneficiary_type') == 'external':
            ben_dept = section.get('beneficiary_department_en', '')
            beneficiary_info = ben_dept[:15] + '...' if len(ben_dept) > 15 else ben_dept

        # Calculate section achievement
        achieved_in_section = sum(1 for c in section_report['report_data'] if c['result'] == 'Achieved')
        total_clos_section = len(section_report['report_data'])

        sections_data.append([
            f"Sec {section.get('section_number', '')}",
            f"{section.get('semester_code', '')} {section.get('academic_year', '')}",
            gender[:6],
            instructor_name[:12] + '...' if len(instructor_name) > 12 else instructor_name,
            str(section_report['regular_count']),
            f"{achieved_in_section}/{total_clos_section}",
            beneficiary_info
        ])

    sections_table = Table(sections_data, colWidths=[1.8*cm, 2.8*cm, 1.5*cm, 3*cm, 1.5*cm, 2.2*cm, 3.5*cm])
    sections_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#4CAF50')),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
    ]))
    elements.append(sections_table)
    elements.append(Spacer(1, 0.2*inch))

    # ===== BENEFICIARY DETAILS (if external sections exist) =====
    external_sections = [s for s in selected_sections if s.get('beneficiary_type') == 'external']
    if external_sections:
        elements.append(Paragraph("Beneficiary Colleges & Departments", section_style))

        ben_header = ['Section', 'Beneficiary College', 'Beneficiary Department']
        ben_data = [ben_header]

        for section in external_sections:
            ben_data.append([
                f"Section {section.get('section_number', '')}",
                section.get('beneficiary_college_en', '')[:25],
                section.get('beneficiary_department_en', '')[:30]
            ])

        ben_table = Table(ben_data, colWidths=[3*cm, 6.5*cm, 6.5*cm])
        ben_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9800')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#FF9800')),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ]))
        elements.append(ben_table)
        elements.append(Spacer(1, 0.2*inch))

    # ===== INDIVIDUAL SECTION REPORTS =====
    elements.append(Paragraph("Individual Section CLO Results", section_style))

    for section_report in sections_reports:
        if section_report is None:
            continue

        section = section_report['section']
        instructor_name = get_instructor_name(section.get('instructor_id'))

        # Section sub-header
        section_header = f"Section {section.get('section_number')} - {section.get('semester_code')} {section.get('academic_year')} | Instructor: {instructor_name} | Students: {section_report['regular_count']}"
        elements.append(Paragraph(section_header, small_style))
        elements.append(Spacer(1, 0.05*inch))

        # CLO Table
        table_data = [['CLO', 'Target %', 'Actual %', 'Result']]
        for clo_data in section_report['report_data']:
            table_data.append([
                clo_data['clo_code'],
                f"{clo_data['target']:.0f}%",
                f"{clo_data['actual_level']:.1f}%",
                clo_data['result']
            ])

        clo_table = Table(table_data, colWidths=[2*cm, 2.5*cm, 2.5*cm, 3*cm])
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]

        # Color result cells
        for i, clo_data in enumerate(section_report['report_data'], 1):
            if clo_data['result'] == 'Achieved':
                table_style.append(('BACKGROUND', (3, i), (3, i), colors.HexColor('#28a745')))
            else:
                table_style.append(('BACKGROUND', (3, i), (3, i), colors.HexColor('#dc3545')))
            table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.white))

        clo_table.setStyle(TableStyle(table_style))
        elements.append(clo_table)
        elements.append(Spacer(1, 0.15*inch))

    # ===== AGGREGATED RESULTS =====
    elements.append(PageBreak())
    elements.append(Paragraph("Collected Results (Weighted Average)", title_style))
    elements.append(Spacer(1, 0.1*inch))

    elements.append(Paragraph(f"Formula: Sum(Students x Actual Level) / Total Students", small_style))
    elements.append(Paragraph(f"Total Students: {total_students} across {valid_sections_count} sections", normal_style))
    elements.append(Spacer(1, 0.2*inch))

    # Collected Table
    agg_table_data = [['CLO', 'Description', 'Target %', 'Weighted Avg %', 'Result']]
    for agg in aggregated_results:
        agg_table_data.append([
            agg['clo_code'],
            agg['clo_description'][:40] + '...' if len(agg['clo_description']) > 40 else agg['clo_description'],
            f"{agg['target']:.0f}%",
            f"{agg['actual_level']:.1f}%",
            agg['result']
        ])

    agg_table = Table(agg_table_data, colWidths=[1.5*cm, 8*cm, 2*cm, 3*cm, 3*cm])
    agg_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]

    for i, agg in enumerate(aggregated_results, 1):
        if agg['result'] == 'Achieved':
            agg_style.append(('BACKGROUND', (4, i), (4, i), colors.HexColor('#28a745')))
        else:
            agg_style.append(('BACKGROUND', (4, i), (4, i), colors.HexColor('#dc3545')))
        agg_style.append(('TEXTCOLOR', (4, i), (4, i), colors.white))

    agg_table.setStyle(TableStyle(agg_style))
    elements.append(agg_table)

    # ===== SUMMARY =====
    elements.append(Spacer(1, 0.3*inch))
    achieved_count = sum(1 for a in aggregated_results if a['result'] == 'Achieved')
    total_clos = len(aggregated_results)
    achievement_rate = (achieved_count/total_clos*100) if total_clos > 0 else 0

    summary_data = [
        ['Summary Statistics', '', '', ''],
        ['Total CLOs', str(total_clos), 'Achieved', str(achieved_count)],
        ['Not Achieved', str(total_clos - achieved_count), 'Achievement Rate', f"{achievement_rate:.1f}%"],
    ]
    summary_table = Table(summary_data, colWidths=[4*cm, 3*cm, 4*cm, 3*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('SPAN', (0, 0), (-1, 0)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBEFORE', (2, 1), (2, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (1, 1), colors.HexColor('#e3f2fd')),
        ('BACKGROUND', (2, 1), (3, 1), colors.HexColor('#e8f5e9')),
        ('BACKGROUND', (0, 2), (1, 2), colors.HexColor('#ffebee')),
        ('BACKGROUND', (2, 2), (3, 2), colors.HexColor('#fff3e0')),
    ]))
    elements.append(summary_table)

    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, textColor=colors.HexColor('#999999'))
    elements.append(Paragraph("Generated by CLO Measurement System", footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def show_aggregated_clo_report(db: Database, user, lang: str):
    """Display Collected CLO Assessment Report"""

    st.title("📊 Collected CLO Assessment Report")
    st.caption("Consolidated CLO measurement across multiple sections")

    # Initialize permissions helper
    perm = get_permissions_helper(db, user)

    # Load data and apply permissions filtering
    sections_data = load_sections_data()
    all_sections = sections_data.get('sections', [])
    sections = perm.filter_sections(all_sections)

    programs_data = load_programs_data()
    all_programs = programs_data.get('programs', [])
    programs = perm.filter_programs(all_programs)

    courses_data = load_courses_data()
    all_courses = courses_data.get('courses', [])
    courses = perm.filter_courses(all_courses)

    if not sections:
        st.warning("No sections found. Please create sections first.")
        return

    # Selection Filters
    st.markdown("### Select Course and Sections")

    # Row 1: Program and Course
    col1, col2 = st.columns(2)

    with col1:
        program_options = ["-- Select Program --"]
        program_map = {}
        for p in programs:
            if p.get('is_active', True):
                display = f"{p.get('program_code', '')} - {p.get('program_name_en', '')}"
                program_options.append(display)
                program_map[display] = p.get('program_id')

        selected_program_display = st.selectbox(
            "Program",
            program_options,
            key="agg_program_filter"
        )

        selected_program_id = None
        if selected_program_display != "-- Select Program --":
            selected_program_id = program_map.get(selected_program_display)

    with col2:
        if selected_program_id:
            program_courses = [c for c in courses if c.get('program_id') == selected_program_id]
            course_options = ["-- Select Course --"]
            course_map = {}
            for c in program_courses:
                display = f"{c.get('course_code', '')} - {c.get('course_title_en', '')}"
                course_options.append(display)
                course_map[display] = c.get('course_id')

            selected_course_display = st.selectbox(
                "Course",
                course_options,
                key="agg_course_filter"
            )

            selected_course_id = None
            if selected_course_display != "-- Select Course --":
                selected_course_id = course_map.get(selected_course_display)
        else:
            st.selectbox(
                "Course",
                ["-- Select Program First --"],
                disabled=True,
                key="agg_course_filter_disabled"
            )
            selected_course_id = None

    if not selected_course_id:
        st.info("💡 Please select a Program and Course to view available sections")
        return

    # Get course data and CLOs
    course_data = get_course_data(selected_course_id)
    clos = get_course_clos(selected_course_id)
    clos_distribution = get_clos_activities_distribution(selected_course_id)

    if not clos:
        st.warning("No CLOs defined for this course. Please define CLOs first.")
        return

    if not clos_distribution:
        st.warning("CLOs distribution not defined. Please complete Stage 2.4 first.")
        return

    # Get all sections for this course
    course_sections = [s for s in sections if s.get('course_id') == selected_course_id]

    if not course_sections:
        st.warning("No sections found for this course.")
        return

    # Row 2: Academic Year and Semester filters
    col3, col4 = st.columns(2)

    with col3:
        # Academic Year filter
        available_years = sorted(list(set(s.get('academic_year', '') for s in course_sections if s.get('academic_year'))), reverse=True)
        year_options = ["-- All Years / كل السنوات --"] + available_years

        selected_year = st.selectbox(
            "Academic Year / السنة الدراسية",
            year_options,
            key="agg_year_filter"
        )

        if selected_year == "-- All Years / كل السنوات --":
            selected_year = None

    with col4:
        # Semester filter
        if selected_year:
            year_sections = [s for s in course_sections if s.get('academic_year') == selected_year]
        else:
            year_sections = course_sections

        available_semesters = sorted(list(set(s.get('semester', '') for s in year_sections if s.get('semester'))))
        semester_options = ["-- All Semesters / كل الفصول --"] + available_semesters

        selected_semester = st.selectbox(
            "Semester / الفصل الدراسي",
            semester_options,
            key="agg_semester_filter"
        )

        if selected_semester == "-- All Semesters / كل الفصول --":
            selected_semester = None

    # Filter sections based on year and semester
    filtered_sections = course_sections
    if selected_year:
        filtered_sections = [s for s in filtered_sections if s.get('academic_year') == selected_year]
    if selected_semester:
        filtered_sections = [s for s in filtered_sections if s.get('semester') == selected_semester]

    if not filtered_sections:
        st.warning("No sections found for the selected criteria.")
        return

    # Multi-select sections
    st.markdown("### Select Sections to Include / اختر الشعب")

    section_options = []
    section_map = {}

    for s in filtered_sections:
        section_num = s.get('section_number', '')
        semester = s.get('semester_code', '')
        year = s.get('academic_year', '')
        instructor_name = get_instructor_name(s.get('instructor_id'))
        gender = s.get('gender', '').split(' / ')[0] if ' / ' in s.get('gender', '') else s.get('gender', '')

        # Get student count
        section_students = get_section_students(s.get('section_id'))
        regular_count = len([st for st in section_students if st.get('status') == 'Regular'])

        option_text = f"Section {section_num} | {semester} {year} | {gender} | {instructor_name} | {regular_count} students"
        section_options.append(option_text)
        section_map[option_text] = s

    selected_section_displays = st.multiselect(
        "Select sections (you can select multiple)",
        section_options,
        key="agg_sections_multiselect"
    )

    if not selected_section_displays:
        st.info("💡 Please select at least one section to generate the report")
        return

    selected_sections = [section_map[d] for d in selected_section_displays]

    # Calculate reports for each section
    sections_reports = []
    for section in selected_sections:
        report = calculate_section_clo_report(section, course_data, clos, clos_distribution)
        sections_reports.append(report)

    # Calculate totals for header
    total_students = sum(sr['regular_count'] for sr in sections_reports if sr)
    valid_sections_count = len([sr for sr in sections_reports if sr])

    # Get program info
    program_data = None
    for p in programs:
        if p.get('program_id') == course_data.get('program_id'):
            program_data = p
            break

    # Check for external/beneficiary sections
    external_sections = [s for s in selected_sections if s.get('beneficiary_type') == 'external']
    has_external = len(external_sections) > 0

    # ===============================
    # Beautiful Report Header (like clo_assessment_report)
    # ===============================
    st.markdown("---")

    # Build beneficiary text
    beneficiary_html = ""
    if has_external:
        # Get unique beneficiaries
        beneficiaries = set()
        for s in external_sections:
            ben_college = s.get('beneficiary_college_en', '')
            ben_dept = s.get('beneficiary_department_en', '')
            if ben_college and ben_dept:
                beneficiaries.add(f"{ben_college} - {ben_dept}")
        if beneficiaries:
            ben_list = " | ".join(list(beneficiaries)[:2])  # Show max 2
            if len(beneficiaries) > 2:
                ben_list += f" (+{len(beneficiaries)-2} more)"
            beneficiary_html = f'<p style="color: #ffd700; margin: 8px 0; font-size: 14px; font-weight: bold;">Beneficiary: {ben_list}</p>'

    # Build period info
    period_info = ""
    if selected_year and selected_semester:
        period_info = f"{selected_semester} {selected_year}"
    elif selected_year:
        period_info = f"Year: {selected_year}"
    elif selected_semester:
        period_info = f"Semester: {selected_semester}"
    else:
        period_info = "All Periods"

    header_html = f"""
    <div style="background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
                padding: 30px; border-radius: 15px; margin-bottom: 25px; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 26px;">Collected CLO Assessment Report</h1>
        <h2 style="color: #bbdefb; margin: 10px 0; font-size: 20px;">التقرير المجمع لقياس مخرجات التعلم</h2>
        <p style="color: white; margin: 10px 0; font-size: 16px;">
            {course_data.get('course_code', '')} - {course_data.get('course_title_en', '')}
        </p>
        <p style="color: #e3f2fd; margin: 5px 0; font-size: 14px;">
            {period_info} | Sections: {valid_sections_count} | Total Students: {total_students}
        </p>
        {beneficiary_html}
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # ===============================
    # Sections Summary Table
    # ===============================
    st.markdown("### 📋 Sections Overview / نظرة عامة على الشعب")

    sections_summary_data = []
    for i, section in enumerate(selected_sections):
        section_report = sections_reports[i]
        if section_report is None:
            continue

        instructor_name = get_instructor_name(section.get('instructor_id'))
        if not instructor_name:
            instructor_name = "Not Assigned"
        gender = section.get('gender', '').split(' / ')[0] if ' / ' in section.get('gender', '') else section.get('gender', 'N/A')

        # Beneficiary info
        beneficiary_info = "Internal"
        if section.get('beneficiary_type') == 'external':
            ben_college = section.get('beneficiary_college_en', '')
            ben_dept = section.get('beneficiary_department_en', '')
            beneficiary_info = f"🏫 {ben_college} - {ben_dept}"

        # Calculate section achievement rate
        achieved_in_section = sum(1 for c in section_report['report_data'] if c['result'] == 'Achieved')
        total_clos_section = len(section_report['report_data'])
        section_achievement_rate = (achieved_in_section / total_clos_section * 100) if total_clos_section > 0 else 0

        sections_summary_data.append({
            'Section': f"Section {section.get('section_number', '')}",
            'Semester': f"{section.get('semester_code', '')} {section.get('academic_year', '')}",
            'Gender': gender,
            'Instructor': instructor_name if len(instructor_name) <= 25 else instructor_name[:22] + '...',
            'Students': section_report['regular_count'],
            'CLOs Achieved': f"{achieved_in_section}/{total_clos_section}",
            'Achievement %': f"{section_achievement_rate:.0f}%",
            'Beneficiary': beneficiary_info if len(beneficiary_info) <= 30 else beneficiary_info[:27] + '...'
        })

    sections_df = pd.DataFrame(sections_summary_data)
    st.dataframe(sections_df, use_container_width=True, hide_index=True)

    # Show beneficiary details if there are external sections
    if has_external:
        st.markdown("#### 🏫 Beneficiary Colleges & Departments / الكليات والأقسام المستفيدة")

        beneficiary_data = []
        for section in external_sections:
            beneficiary_data.append({
                'Section': f"Section {section.get('section_number', '')}",
                'Beneficiary College': section.get('beneficiary_college_en', section.get('beneficiary_college_ar', '')),
                'Beneficiary Department': section.get('beneficiary_department_en', section.get('beneficiary_department_ar', '')),
                'Semester': f"{section.get('semester_code', '')} {section.get('academic_year', '')}"
            })

        if beneficiary_data:
            beneficiary_df = pd.DataFrame(beneficiary_data)
            st.dataframe(beneficiary_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Display individual section reports
    st.markdown("### 📑 Individual Section Reports / تقارير الشعب الفردية")

    # Build section options for selectbox
    section_options = []
    section_reports_map = {}

    for idx, section_report in enumerate(sections_reports):
        if section_report is None:
            continue

        section = section_report['section']
        section_num = section.get('section_number', 'N/A')
        semester_code = section.get('semester_code', '')
        academic_year = section.get('academic_year', '')

        # Calculate section achievement
        achieved_in_section = sum(1 for c in section_report['report_data'] if c['result'] == 'Achieved')
        total_clos_section = len(section_report['report_data'])
        section_achievement_rate = (achieved_in_section / total_clos_section * 100) if total_clos_section > 0 else 0

        # Determine achievement status
        achievement_icon = "✅" if section_achievement_rate >= 70 else "⚠️" if section_achievement_rate >= 50 else "❌"

        # Build option label
        option_label = f"Section {section_num} | {semester_code} {academic_year} | {achievement_icon} {section_achievement_rate:.0f}% ({section_report['regular_count']} students)"
        section_options.append(option_label)
        section_reports_map[option_label] = section_report

    if section_options:
        selected_section_option = st.selectbox(
            "Select a section to view details:",
            section_options,
            key="individual_section_select"
        )

        if selected_section_option:
            section_report = section_reports_map[selected_section_option]
            section = section_report['section']

            instructor_name = get_instructor_name(section.get('instructor_id'))
            if not instructor_name:
                instructor_name = "Not Assigned"
            gender = section.get('gender', '').split(' / ')[0] if ' / ' in section.get('gender', '') else section.get('gender', 'N/A')

            achieved_in_section = sum(1 for c in section_report['report_data'] if c['result'] == 'Achieved')
            total_clos_section = len(section_report['report_data'])

            # Section details in columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**👨‍🏫 Instructor:** {instructor_name}")
            with col2:
                st.markdown(f"**👥 Gender:** {gender}")
            with col3:
                st.markdown(f"**📊 CLOs Achieved:** {achieved_in_section}/{total_clos_section}")

            # Beneficiary info if external
            if section.get('beneficiary_type') == 'external':
                ben_college = section.get('beneficiary_college_en', '')
                ben_dept = section.get('beneficiary_department_en', '')
                st.info(f"🏫 **Beneficiary:** {ben_college} - {ben_dept}")

            # Create DataFrame for display
            df_data = []
            for clo_data in section_report['report_data']:
                df_data.append({
                    'CLO': clo_data['clo_code'],
                    'Target %': f"{clo_data['target']:.0f}%",
                    'Criterion %': f"{clo_data['criterion']:.0f}%",
                    'Actual Level %': f"{clo_data['actual_level']:.1f}%",
                    'Students Achieved': f"{clo_data['students_achieved']}/{clo_data['total_students']}",
                    'Result': '✅ Achieved' if clo_data['result'] == 'Achieved' else '❌ Not Achieved'
                })

            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # Calculate and display aggregated results
    st.markdown("---")
    st.markdown("### 2. Assessment Results / نتائج التقييم")

    aggregated_results = calculate_aggregated_results(sections_reports, clos)

    # Group CLOs by domain (extract domain from CLO code like K1, S1, V1, CLO1, etc.)
    domain_names = {
        'K': '1 Knowledge and Understanding',
        'S': '2 Skills',
        'V': '3 Values',
        'O': 'Course Learning Outcomes'
    }

    def get_domain_key(clo_code):
        clo_code_upper = clo_code.upper()
        if clo_code_upper.startswith('K') or 'K1' in clo_code_upper or 'K2' in clo_code_upper:
            return 'K'
        elif clo_code_upper.startswith('S') or 'S1' in clo_code_upper or 'S2' in clo_code_upper:
            return 'S'
        elif clo_code_upper.startswith('V') or 'V1' in clo_code_upper or 'V2' in clo_code_upper:
            return 'V'
        return 'O'

    # Group results by domain
    domains = {}
    for agg in aggregated_results:
        domain_key = get_domain_key(agg['clo_code'])
        if domain_key not in domains:
            domains[domain_key] = []
        domains[domain_key].append(agg)

    # Check if we need domain headers
    show_domain_headers = len(domains) > 1 or 'O' not in domains

    # Display results grouped by domain
    domain_order = ['K', 'S', 'V', 'O']

    for domain_key in domain_order:
        if domain_key not in domains:
            continue

        domain_name = domain_names.get(domain_key, 'Course Learning Outcomes')

        # Show domain header
        if show_domain_headers:
            st.markdown(f"""
            <div style="background-color: #4CAF50; color: white; padding: 10px 15px;
                        border-radius: 5px; margin: 15px 0 10px 0; font-weight: bold; text-align: center;">
                {domain_name}
            </div>
            """, unsafe_allow_html=True)

        # Create DataFrame for this domain
        domain_data = []
        for agg in domains[domain_key]:
            description = agg['clo_description']
            if len(description) > 70:
                description = description[:67] + '...'

            domain_data.append({
                'Course Learning Outcomes': description,
                'CLO Code': agg['clo_code'],
                'Criterion %': f"{agg['criterion']:.0f}%",
                'Target %': f"{agg['target']:.0f}%",
                'Actual %': f"{agg['actual_level']:.1f}%",
                'Result': '✅ Achieved' if agg['result'] == 'Achieved' else '❌ Not Achieved'
            })

        domain_df = pd.DataFrame(domain_data)
        st.dataframe(domain_df, use_container_width=True, hide_index=True)

    # Info about weighted average
    st.info(f"📊 **Weighted Average Calculation:** Total {total_students} students across {valid_sections_count} sections")

    # Summary Statistics
    st.markdown("---")
    achieved_count = sum(1 for a in aggregated_results if a['result'] == 'Achieved')
    total_clos = len(aggregated_results)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 15px; border-radius: 10px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Total CLOs</p>
            <p style="color: white; margin: 0; font-size: 28px; font-weight: bold;">{total_clos}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                    padding: 15px; border-radius: 10px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Achieved</p>
            <p style="color: white; margin: 0; font-size: 28px; font-weight: bold;">{achieved_count}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
                    padding: 15px; border-radius: 10px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Not Achieved</p>
            <p style="color: white; margin: 0; font-size: 28px; font-weight: bold;">{total_clos - achieved_count}</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        achievement_rate = (achieved_count / total_clos * 100) if total_clos > 0 else 0
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
                    padding: 15px; border-radius: 10px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Achievement Rate</p>
            <p style="color: white; margin: 0; font-size: 28px; font-weight: bold;">{achievement_rate:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    # Export Options
    st.markdown("---")
    st.markdown("### 💾 Export Report")

    col1, col2 = st.columns(2)

    with col1:
        # Excel Export
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Collected results
            agg_df = pd.DataFrame([{
                'CLO': a['clo_code'],
                'Description': a['clo_description'],
                'Target %': a['target'],
                'Weighted Avg %': round(a['actual_level'], 1),
                'Result': a['result']
            } for a in aggregated_results])
            agg_df.to_excel(writer, index=False, sheet_name='Collected Results')

            # Individual section results
            for section_report in sections_reports:
                if section_report is None:
                    continue
                section = section_report['section']
                sheet_name = f"Sec {section.get('section_number')}"[:31]

                section_df = pd.DataFrame([{
                    'CLO': c['clo_code'],
                    'Target %': c['target'],
                    'Actual %': round(c['actual_level'], 1),
                    'Students Achieved': c['students_achieved'],
                    'Total Students': c['total_students'],
                    'Result': c['result']
                } for c in section_report['report_data']])
                section_df.to_excel(writer, index=False, sheet_name=sheet_name)

        output.seek(0)
        st.download_button(
            label="📥 Download Excel",
            data=output,
            file_name=f"Collected_CLO_Report_{course_data.get('course_code', '')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )

    with col2:
        # PDF Export
        if PDF_AVAILABLE:
            pdf_data = generate_aggregated_pdf_report(
                course_data, selected_sections, sections_reports, aggregated_results, clos, program_data
            )
            if pdf_data:
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_data,
                    file_name=f"Collected_CLO_Report_{course_data.get('course_code', '')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="secondary"
                )
        else:
            st.warning("PDF export requires reportlab. Install with: pip install reportlab")

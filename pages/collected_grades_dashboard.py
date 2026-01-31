"""
لوحة بيانات درجات الطلاب المجمعة
Collected Grades Dashboard - Multiple Sections
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from io import BytesIO
from models.database import Database, UserRole
from utils.permissions import get_permissions_helper
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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


# Grade scale configuration
GRADE_SCALE = [
    {"min": 95, "max": 100, "grade": "Exceptional", "code": "A+", "color": "#1B5E20"},
    {"min": 90, "max": 94.99, "grade": "Excellent", "code": "A", "color": "#2E7D32"},
    {"min": 85, "max": 89.99, "grade": "Superior", "code": "B+", "color": "#388E3C"},
    {"min": 80, "max": 84.99, "grade": "Very Good", "code": "B", "color": "#43A047"},
    {"min": 75, "max": 79.99, "grade": "Above Average", "code": "C+", "color": "#7CB342"},
    {"min": 70, "max": 74.99, "grade": "Good", "code": "C", "color": "#C0CA33"},
    {"min": 65, "max": 69.99, "grade": "High Pass", "code": "D+", "color": "#FDD835"},
    {"min": 60, "max": 64.99, "grade": "Pass", "code": "D", "color": "#FFB300"},
    {"min": 0, "max": 59.99, "grade": "Fail", "code": "F", "color": "#E53935"},
]


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


def calculate_student_total(student_id, grades, clos_distribution):
    """Calculate total marks for a student"""
    total = 0
    for activity_name, clo_marks in clos_distribution.items():
        for clo_code, max_mark in clo_marks.items():
            if max_mark > 0:
                key = f"{activity_name}_{clo_code}"
                total += grades.get(student_id, {}).get(key, 0)
    return total


def calculate_max_total(clos_distribution):
    """Calculate maximum possible total"""
    total = 0
    for activity_name, clo_marks in clos_distribution.items():
        for clo_code, max_mark in clo_marks.items():
            total += max_mark
    return total


def get_grade_info(percentage):
    """Get grade information based on percentage"""
    for grade in GRADE_SCALE:
        if grade["min"] <= percentage <= grade["max"]:
            return grade
    return GRADE_SCALE[-1]  # Return Fail as default


def calculate_section_grades_report(section, clos_distribution):
    """Calculate grades report data for a single section"""
    section_id = section.get('section_id')

    section_students = get_section_students(section_id)
    grades = get_section_grades(section_id)

    regular_students = [s for s in section_students if s.get('status') == 'Regular']
    dropped_students = [s for s in section_students if s.get('status') == 'Dropped']
    prohibited_students = [s for s in section_students if s.get('status') == 'Prohibited']
    incomplete_students = [s for s in section_students if s.get('status') == 'Incomplete']

    regular_count = len(regular_students)

    if regular_count == 0:
        return None

    max_total = calculate_max_total(clos_distribution)

    if max_total == 0:
        return None

    # Calculate student results
    student_results = []
    percentages = []

    for student in regular_students:
        student_id = student.get('student_record_id')
        total_marks = calculate_student_total(student_id, grades, clos_distribution)
        percentage = (total_marks / max_total * 100) if max_total > 0 else 0
        grade_info = get_grade_info(percentage)

        student_results.append({
            'section_id': section_id,
            'section_number': section.get('section_number', ''),
            'student_record_id': student_id,
            'student_no': student.get('student_no'),
            'student_name': student.get('student_name'),
            'total_marks': total_marks,
            'max_marks': max_total,
            'percentage': percentage,
            'grade': grade_info['grade'],
            'grade_code': grade_info['code'],
            'color': grade_info['color']
        })
        percentages.append(percentage)

    # Calculate statistics
    if percentages:
        mean_pct = sum(percentages) / len(percentages)
        sorted_pct = sorted(percentages)
        n = len(sorted_pct)
        median_pct = sorted_pct[n // 2] if n % 2 == 1 else (sorted_pct[n // 2 - 1] + sorted_pct[n // 2]) / 2 if n > 0 else 0
        min_pct = min(percentages)
        max_pct = max(percentages)

        if len(percentages) > 1:
            variance = sum((x - mean_pct) ** 2 for x in percentages) / len(percentages)
            std_pct = variance ** 0.5
        else:
            std_pct = 0

        pass_count = sum(1 for p in percentages if p >= 60)
        fail_count = len(percentages) - pass_count
        pass_rate = (pass_count / len(percentages) * 100) if percentages else 0

        # Coefficient of Variation (CV) = (Std Dev / Mean) * 100
        cv = (std_pct / mean_pct * 100) if mean_pct > 0 else 0
    else:
        mean_pct = median_pct = min_pct = max_pct = std_pct = 0
        pass_count = fail_count = 0
        pass_rate = cv = 0

    # Count by grade
    grade_counts = {}
    for grade in GRADE_SCALE:
        grade_counts[grade['code']] = sum(1 for r in student_results if r['grade_code'] == grade['code'])

    return {
        'section': section,
        'regular_count': regular_count,
        'dropped_count': len(dropped_students),
        'prohibited_count': len(prohibited_students),
        'incomplete_count': len(incomplete_students),
        'total_count': len(section_students),
        'max_total': max_total,
        'student_results': student_results,
        'statistics': {
            'mean': mean_pct,
            'median': median_pct,
            'min': min_pct,
            'max': max_pct,
            'std': std_pct,
            'cv': cv,
            'pass_count': pass_count,
            'fail_count': fail_count,
            'pass_rate': pass_rate
        },
        'grade_counts': grade_counts
    }


def calculate_collected_statistics(sections_reports):
    """Calculate weighted statistics across all sections"""
    all_percentages = []
    total_regular = 0
    total_dropped = 0
    total_prohibited = 0
    total_incomplete = 0
    total_all = 0
    all_student_results = []

    for report in sections_reports:
        if report is None:
            continue

        total_regular += report['regular_count']
        total_dropped += report['dropped_count']
        total_prohibited += report['prohibited_count']
        total_incomplete += report['incomplete_count']
        total_all += report['total_count']

        for result in report['student_results']:
            all_percentages.append(result['percentage'])
            all_student_results.append(result)

    if not all_percentages:
        return None

    # Calculate overall statistics
    mean_pct = sum(all_percentages) / len(all_percentages)
    sorted_pct = sorted(all_percentages)
    n = len(sorted_pct)
    median_pct = sorted_pct[n // 2] if n % 2 == 1 else (sorted_pct[n // 2 - 1] + sorted_pct[n // 2]) / 2 if n > 0 else 0
    min_pct = min(all_percentages)
    max_pct = max(all_percentages)

    if len(all_percentages) > 1:
        variance = sum((x - mean_pct) ** 2 for x in all_percentages) / len(all_percentages)
        std_pct = variance ** 0.5
    else:
        std_pct = 0

    pass_count = sum(1 for p in all_percentages if p >= 60)
    fail_count = len(all_percentages) - pass_count
    pass_rate = (pass_count / len(all_percentages) * 100) if all_percentages else 0

    # Coefficient of Variation (CV) = (Std Dev / Mean) * 100
    cv = (std_pct / mean_pct * 100) if mean_pct > 0 else 0

    # Count by grade
    grade_counts = {}
    for grade in GRADE_SCALE:
        grade_counts[grade['code']] = sum(1 for r in all_student_results if r['grade_code'] == grade['code'])

    return {
        'total_regular': total_regular,
        'total_dropped': total_dropped,
        'total_prohibited': total_prohibited,
        'total_incomplete': total_incomplete,
        'total_all': total_all,
        'statistics': {
            'mean': mean_pct,
            'median': median_pct,
            'min': min_pct,
            'max': max_pct,
            'std': std_pct,
            'cv': cv,
            'pass_count': pass_count,
            'fail_count': fail_count,
            'pass_rate': pass_rate
        },
        'grade_counts': grade_counts,
        'all_student_results': all_student_results
    }


def generate_collected_grades_pdf(course_data, selected_sections, sections_reports, collected_stats, program_data=None):
    """Generate PDF report for collected grades dashboard"""
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
    elements.append(Paragraph("Collected Grades Dashboard", title_style))
    elements.append(Paragraph("Consolidated Student Performance Analysis", subtitle_style))
    elements.append(Spacer(1, 0.3*inch))

    # ===== COURSE INFO =====
    valid_sections_count = len([sr for sr in sections_reports if sr])

    info_data = [
        ['Course Code', course_data.get('course_code', '')],
        ['Course Title', course_data.get('course_title_en', '')],
        ['Program', program_data.get('program_name_en', 'N/A') if program_data else 'N/A'],
        ['Total Sections', str(valid_sections_count)],
        ['Total Students', str(collected_stats['total_regular'])],
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

    # ===== STUDENT STATUS =====
    elements.append(Paragraph("Student Status Summary", section_style))
    status_data = [
        ['Total', 'Regular', 'Dropped', 'Prohibited', 'Incomplete'],
        [str(collected_stats['total_all']), str(collected_stats['total_regular']),
         str(collected_stats['total_dropped']), str(collected_stats['total_prohibited']),
         str(collected_stats['total_incomplete'])]
    ]
    status_colors = ['#2196F3', '#4CAF50', '#FF9800', '#f44336', '#9C27B0']
    status_table = Table(status_data, colWidths=[3.6*cm]*5)
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(status_colors[0])),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor(status_colors[1])),
        ('BACKGROUND', (2, 0), (2, 0), colors.HexColor(status_colors[2])),
        ('BACKGROUND', (3, 0), (3, 0), colors.HexColor(status_colors[3])),
        ('BACKGROUND', (4, 0), (4, 0), colors.HexColor(status_colors[4])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, 1), 16),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
    ]))
    elements.append(status_table)
    elements.append(Spacer(1, 0.3*inch))

    # ===== KEY STATISTICS =====
    elements.append(Paragraph("Key Statistics (All Sections)", section_style))
    stats = collected_stats['statistics']
    stats_data = [
        ['Mean', 'Median', 'Std Dev', 'CV', 'Min', 'Max', 'Pass Rate'],
        [f"{stats['mean']:.1f}%", f"{stats['median']:.1f}%", f"{stats['std']:.1f}%",
         f"{stats['cv']:.1f}%", f"{stats['min']:.1f}%", f"{stats['max']:.1f}%", f"{stats['pass_rate']:.1f}%"]
    ]
    stats_table = Table(stats_data, colWidths=[2.5*cm]*7)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8f9fa')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, 1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#667eea')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#667eea')),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 0.3*inch))

    # ===== SECTIONS SUMMARY =====
    elements.append(Paragraph("Sections Performance Summary", section_style))

    sections_header = ['Section', 'Semester', 'Instructor', 'Students', 'Mean', 'Std', 'CV', 'Pass Rate']
    sections_data = [sections_header]

    for i, section in enumerate(selected_sections):
        section_report = sections_reports[i]
        if section_report is None:
            continue

        instructor_name = get_instructor_name(section.get('instructor_id'))
        if not instructor_name:
            instructor_name = "Not Assigned"

        sections_data.append([
            f"Sec {section.get('section_number', '')}",
            f"{section.get('semester_code', '')} {section.get('academic_year', '')}",
            instructor_name[:12] + '..' if len(instructor_name) > 12 else instructor_name,
            str(section_report['regular_count']),
            f"{section_report['statistics']['mean']:.1f}%",
            f"{section_report['statistics']['std']:.1f}%",
            f"{section_report['statistics']['cv']:.1f}%",
            f"{section_report['statistics']['pass_rate']:.1f}%"
        ])

    sections_table = Table(sections_data, colWidths=[1.8*cm, 2.5*cm, 3*cm, 1.5*cm, 2*cm, 1.8*cm, 1.8*cm, 2*cm])
    sections_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#4CAF50')),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
    ]))
    elements.append(sections_table)
    elements.append(Spacer(1, 0.3*inch))

    # ===== GRADE BREAKDOWN =====
    elements.append(Paragraph("Grade Distribution (All Sections)", section_style))
    grade_data = [['Grade', 'Code', 'Range', 'Count', '%']]
    total_students = collected_stats['total_regular']

    for grade in GRADE_SCALE:
        count = collected_stats['grade_counts'].get(grade['code'], 0)
        pct = (count / total_students * 100) if total_students > 0 else 0
        grade_data.append([grade['grade'], grade['code'], f"{grade['min']}-{grade['max']}%", str(count), f"{pct:.1f}%"])

    grade_table = Table(grade_data, colWidths=[4.5*cm, 2*cm, 4*cm, 3*cm, 3*cm])
    grade_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
    ]
    for i, grade in enumerate(GRADE_SCALE):
        grade_style.append(('BACKGROUND', (1, i+1), (1, i+1), colors.HexColor(grade['color'])))
        grade_style.append(('TEXTCOLOR', (1, i+1), (1, i+1), colors.white))

    grade_table.setStyle(TableStyle(grade_style))
    elements.append(grade_table)

    # ===== STUDENT RESULTS =====
    elements.append(PageBreak())
    elements.append(Paragraph("All Student Results", title_style))
    elements.append(Spacer(1, 0.2*inch))

    results_data = [['Rank', 'Section', 'Student No', 'Student Name', 'Total', '%', 'Grade']]
    sorted_results = sorted(collected_stats['all_student_results'], key=lambda x: x['percentage'], reverse=True)

    for i, row in enumerate(sorted_results, 1):
        results_data.append([
            str(i),
            f"Sec {row['section_number']}",
            str(row['student_no']),
            str(row['student_name'])[:20],
            f"{row['total_marks']:.1f}",
            f"{row['percentage']:.1f}%",
            row['grade_code']
        ])

    results_table = Table(results_data, colWidths=[1.2*cm, 1.8*cm, 2.5*cm, 5*cm, 2*cm, 2*cm, 1.5*cm])
    results_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (3, 1), (3, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1565c0')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#1565c0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
    ]

    for i, row in enumerate(sorted_results, 1):
        grade_info = get_grade_info(row['percentage'])
        results_style.append(('BACKGROUND', (6, i), (6, i), colors.HexColor(grade_info['color'])))
        results_style.append(('TEXTCOLOR', (6, i), (6, i), colors.white))

    results_table.setStyle(TableStyle(results_style))
    elements.append(results_table)

    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, textColor=colors.HexColor('#999999'))
    elements.append(Paragraph("Generated by CLO Measurement System", footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def show_collected_grades_dashboard(db: Database, user, lang: str):
    """Display Collected Grades Dashboard"""

    st.title("📊 Collected Grades Dashboard")
    st.caption("Consolidated student grades analysis across multiple sections")

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
            key="coll_grades_program_filter"
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
                key="coll_grades_course_filter"
            )

            selected_course_id = None
            if selected_course_display != "-- Select Course --":
                selected_course_id = course_map.get(selected_course_display)
        else:
            st.selectbox(
                "Course",
                ["-- Select Program First --"],
                disabled=True,
                key="coll_grades_course_filter_disabled"
            )
            selected_course_id = None

    if not selected_course_id:
        st.info("Please select a Program and Course to view available sections")
        return

    # Get course data
    course_data = get_course_data(selected_course_id)
    clos_distribution = get_clos_activities_distribution(selected_course_id)

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
            key="coll_grades_year_filter"
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
            key="coll_grades_semester_filter"
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
        key="coll_grades_sections_multiselect"
    )

    if not selected_section_displays:
        st.info("Please select at least one section to generate the dashboard")
        return

    selected_sections = [section_map[d] for d in selected_section_displays]

    # Calculate reports for each section
    sections_reports = []
    for section in selected_sections:
        report = calculate_section_grades_report(section, clos_distribution)
        sections_reports.append(report)

    # Calculate collected statistics
    collected_stats = calculate_collected_statistics(sections_reports)

    if collected_stats is None:
        st.warning("No valid grades data found for the selected sections.")
        return

    # Get program info
    program_data = None
    for p in programs:
        if p.get('program_id') == course_data.get('program_id'):
            program_data = p
            break

    valid_sections_count = len([sr for sr in sections_reports if sr])

    # ===============================
    # Beautiful Report Header
    # ===============================
    st.markdown("---")

    # Check for external sections
    external_sections = [s for s in selected_sections if s.get('beneficiary_type') == 'external']
    has_external = len(external_sections) > 0

    beneficiary_html = ""
    if has_external:
        beneficiaries = set()
        for s in external_sections:
            ben_college = s.get('beneficiary_college_en', '')
            ben_dept = s.get('beneficiary_department_en', '')
            if ben_college and ben_dept:
                beneficiaries.add(f"{ben_college} - {ben_dept}")
        if beneficiaries:
            ben_list = " | ".join(list(beneficiaries)[:2])
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
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px; border-radius: 15px; margin-bottom: 25px; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 26px;">Collected Grades Dashboard</h1>
        <h2 style="color: #e0e0e0; margin: 10px 0; font-size: 18px;">لوحة بيانات الدرجات المجمعة</h2>
        <p style="color: white; margin: 10px 0; font-size: 16px;">
            {course_data.get('course_code', '')} - {course_data.get('course_title_en', '')}
        </p>
        <p style="color: #e8e8e8; margin: 5px 0; font-size: 14px;">
            {period_info} | Sections: {valid_sections_count} | Total Students: {collected_stats['total_regular']}
        </p>
        {beneficiary_html}
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # ===============================
    # Student Status Statistics
    # ===============================
    st.markdown("### 👥 Student Status / حالة الطلاب")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Total / الإجمالي</p>
            <p style="color: white; margin: 0; font-size: 36px; font-weight: bold; line-height: 1.2;">{collected_stats['total_all']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Regular / منتظم</p>
            <p style="color: white; margin: 0; font-size: 36px; font-weight: bold; line-height: 1.2;">{collected_stats['total_regular']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Dropped / معتذر</p>
            <p style="color: white; margin: 0; font-size: 36px; font-weight: bold; line-height: 1.2;">{collected_stats['total_dropped']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Prohibited / محروم</p>
            <p style="color: white; margin: 0; font-size: 36px; font-weight: bold; line-height: 1.2;">{collected_stats['total_prohibited']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Incomplete / غير مكمل</p>
            <p style="color: white; margin: 0; font-size: 36px; font-weight: bold; line-height: 1.2;">{collected_stats['total_incomplete']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ===============================
    # Key Statistics Cards (Collected)
    # ===============================
    st.markdown("### 📈 Collected Statistics / الإحصائيات المجمعة")

    stats = collected_stats['statistics']

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 11px;">Mean / المتوسط</p>
            <p style="color: white; margin: 0; font-size: 24px; font-weight: bold; line-height: 1.2;">{stats['mean']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 11px;">Median / الوسيط</p>
            <p style="color: white; margin: 0; font-size: 24px; font-weight: bold; line-height: 1.2;">{stats['median']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 11px;">Std Dev / الانحراف</p>
            <p style="color: white; margin: 0; font-size: 24px; font-weight: bold; line-height: 1.2;">{stats['std']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FF6B6B 0%, #ee5a24 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 11px;">CV / معامل الاختلاف</p>
            <p style="color: white; margin: 0; font-size: 24px; font-weight: bold; line-height: 1.2;">{stats['cv']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 11px;">Min / أدنى</p>
            <p style="color: white; margin: 0; font-size: 24px; font-weight: bold; line-height: 1.2;">{stats['min']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 11px;">Max / أعلى</p>
            <p style="color: white; margin: 0; font-size: 24px; font-weight: bold; line-height: 1.2;">{stats['max']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with col7:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: #333; margin: 0; font-size: 11px;">Pass Rate / نسبة النجاح</p>
            <p style="color: #333; margin: 0; font-size: 24px; font-weight: bold; line-height: 1.2;">{stats['pass_rate']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ===============================
    # Sections Performance Summary
    # ===============================
    st.markdown("### 📋 Sections Performance / أداء الشعب")

    sections_summary_data = []
    for i, section in enumerate(selected_sections):
        section_report = sections_reports[i]
        if section_report is None:
            continue

        instructor_name = get_instructor_name(section.get('instructor_id'))
        if not instructor_name:
            instructor_name = "Not Assigned"
        gender = section.get('gender', '').split(' / ')[0] if ' / ' in section.get('gender', '') else section.get('gender', 'N/A')

        beneficiary_info = "Internal"
        if section.get('beneficiary_type') == 'external':
            ben_dept = section.get('beneficiary_department_en', '')
            beneficiary_info = f"{ben_dept}"

        sec_stats = section_report['statistics']

        sections_summary_data.append({
            'Section': f"Section {section.get('section_number', '')}",
            'Semester': f"{section.get('semester_code', '')} {section.get('academic_year', '')}",
            'Gender': gender,
            'Instructor': instructor_name if len(instructor_name) <= 20 else instructor_name[:17] + '...',
            'Students': section_report['regular_count'],
            'Mean %': f"{sec_stats['mean']:.1f}%",
            'Std %': f"{sec_stats['std']:.1f}%",
            'CV %': f"{sec_stats['cv']:.1f}%",
            'Pass Rate': f"{sec_stats['pass_rate']:.1f}%",
            'Beneficiary': beneficiary_info if len(beneficiary_info) <= 20 else beneficiary_info[:17] + '...'
        })

    sections_df = pd.DataFrame(sections_summary_data)
    st.dataframe(sections_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ===============================
    # Charts Section
    # ===============================
    st.markdown("### 📊 Visual Analytics / التحليل البصري")

    # Row 1: Grade Distribution and Pass/Fail Pie
    col1, col2 = st.columns([2, 1])

    with col1:
        # Grade Distribution Bar Chart
        grade_counts = collected_stats['grade_counts']

        fig_bar = go.Figure(data=[
            go.Bar(
                x=[g['code'] for g in GRADE_SCALE],
                y=[grade_counts.get(g['code'], 0) for g in GRADE_SCALE],
                marker_color=[g['color'] for g in GRADE_SCALE],
                text=[grade_counts.get(g['code'], 0) for g in GRADE_SCALE],
                textposition='outside',
                textfont=dict(size=14, color='white')
            )
        ])

        fig_bar.update_layout(
            title=dict(
                text="Grade Distribution (All Sections)",
                font=dict(size=18, color='white'),
                x=0.5
            ),
            xaxis_title="Grade Code",
            yaxis_title="Number of Students",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.2)'),
            height=400
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # Pass/Fail Pie Chart
        fig_pie = go.Figure(data=[
            go.Pie(
                labels=['Pass / ناجح', 'Fail / راسب'],
                values=[stats['pass_count'], stats['fail_count']],
                marker_colors=['#28a745', '#dc3545'],
                hole=0.4,
                textinfo='label+percent+value',
                textfont=dict(size=12)
            )
        ])

        fig_pie.update_layout(
            title=dict(
                text="Pass/Fail Ratio",
                font=dict(size=16, color='white'),
                x=0.5
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    # Row 2: Section Comparison
    st.markdown("#### Section Comparison / مقارنة الشعب")

    section_names = []
    section_means = []
    section_pass_rates = []

    for i, section in enumerate(selected_sections):
        section_report = sections_reports[i]
        if section_report is None:
            continue
        section_names.append(f"Sec {section.get('section_number', '')}")
        section_means.append(section_report['statistics']['mean'])
        section_pass_rates.append(section_report['statistics']['pass_rate'])

    col1, col2 = st.columns(2)

    with col1:
        fig_mean = go.Figure(data=[
            go.Bar(
                x=section_names,
                y=section_means,
                marker_color='#667eea',
                text=[f"{m:.1f}%" for m in section_means],
                textposition='outside'
            )
        ])

        fig_mean.update_layout(
            title=dict(text="Mean Score by Section", font=dict(size=16, color='white'), x=0.5),
            yaxis_title="Mean %",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.2)'),
            height=350
        )

        st.plotly_chart(fig_mean, use_container_width=True)

    with col2:
        fig_pass = go.Figure(data=[
            go.Bar(
                x=section_names,
                y=section_pass_rates,
                marker_color='#28a745',
                text=[f"{p:.1f}%" for p in section_pass_rates],
                textposition='outside'
            )
        ])

        fig_pass.update_layout(
            title=dict(text="Pass Rate by Section", font=dict(size=16, color='white'), x=0.5),
            yaxis_title="Pass Rate %",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.2)'),
            height=350
        )

        st.plotly_chart(fig_pass, use_container_width=True)

    st.markdown("---")

    # ===============================
    # Individual Section Details
    # ===============================
    st.markdown("### 📑 Individual Section Details / تفاصيل الشعب")

    section_options = []
    section_reports_map = {}

    for idx, section_report in enumerate(sections_reports):
        if section_report is None:
            continue

        section = section_report['section']
        section_num = section.get('section_number', 'N/A')
        semester_code = section.get('semester_code', '')
        academic_year = section.get('academic_year', '')
        sec_stats = section_report['statistics']

        option_label = f"Section {section_num} | {semester_code} {academic_year} | Mean: {sec_stats['mean']:.1f}% | Pass: {sec_stats['pass_rate']:.1f}%"
        section_options.append(option_label)
        section_reports_map[option_label] = section_report

    if section_options:
        selected_section_option = st.selectbox(
            "Select a section to view details:",
            section_options,
            key="individual_grades_section_select"
        )

        if selected_section_option:
            section_report = section_reports_map[selected_section_option]
            section = section_report['section']
            sec_stats = section_report['statistics']

            instructor_name = get_instructor_name(section.get('instructor_id'))
            if not instructor_name:
                instructor_name = "Not Assigned"

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"**Instructor:** {instructor_name}")
            with col2:
                st.markdown(f"**Students:** {section_report['regular_count']}")
            with col3:
                st.markdown(f"**Mean:** {sec_stats['mean']:.1f}%")
            with col4:
                st.markdown(f"**CV:** {sec_stats['cv']:.1f}%")
            with col5:
                st.markdown(f"**Pass Rate:** {sec_stats['pass_rate']:.1f}%")

            # Student results for this section
            df_data = []
            sorted_results = sorted(section_report['student_results'], key=lambda x: x['percentage'], reverse=True)
            for i, result in enumerate(sorted_results, 1):
                df_data.append({
                    'Rank': i,
                    'Student No': result['student_no'],
                    'Student Name': result['student_name'],
                    'Total Marks': f"{result['total_marks']:.1f}/{result['max_marks']}",
                    'Percentage': f"{result['percentage']:.1f}%",
                    'Grade': result['grade_code'],
                    'Grade Name': result['grade']
                })

            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True, height=300)

    st.markdown("---")

    # ===============================
    # All Students Results
    # ===============================
    st.markdown("### 📝 All Students Results / نتائج جميع الطلاب")

    sorted_all_results = sorted(collected_stats['all_student_results'], key=lambda x: x['percentage'], reverse=True)

    all_df_data = []
    for i, result in enumerate(sorted_all_results, 1):
        all_df_data.append({
            'Rank': i,
            'Section': f"Sec {result['section_number']}",
            'Student No': result['student_no'],
            'Student Name': result['student_name'],
            'Total Marks': f"{result['total_marks']:.1f}/{result['max_marks']}",
            'Percentage': f"{result['percentage']:.1f}%",
            'Grade': result['grade_code']
        })

    all_df = pd.DataFrame(all_df_data)
    st.dataframe(all_df, use_container_width=True, height=400)

    st.markdown("---")

    # ===============================
    # Export Options
    # ===============================
    st.markdown("### 💾 Export Report / تصدير التقرير")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Excel Export
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Collected summary
            summary_df = pd.DataFrame([{
                'Course': f"{course_data.get('course_code', '')} - {course_data.get('course_title_en', '')}",
                'Total Sections': valid_sections_count,
                'Total Students': collected_stats['total_regular'],
                'Mean': f"{stats['mean']:.1f}%",
                'Median': f"{stats['median']:.1f}%",
                'Std Dev': f"{stats['std']:.1f}%",
                'CV': f"{stats['cv']:.1f}%",
                'Pass Rate': f"{stats['pass_rate']:.1f}%"
            }])
            summary_df.to_excel(writer, index=False, sheet_name='Summary')

            # Sections performance
            pd.DataFrame(sections_summary_data).to_excel(writer, index=False, sheet_name='Sections')

            # All students
            all_df.to_excel(writer, index=False, sheet_name='All Students')

            # Individual section sheets
            for section_report in sections_reports:
                if section_report is None:
                    continue
                section = section_report['section']
                sheet_name = f"Sec {section.get('section_number')}"[:31]

                section_df = pd.DataFrame([{
                    'Rank': i+1,
                    'Student No': r['student_no'],
                    'Student Name': r['student_name'],
                    'Total Marks': r['total_marks'],
                    'Percentage': f"{r['percentage']:.1f}%",
                    'Grade': r['grade_code']
                } for i, r in enumerate(sorted(section_report['student_results'], key=lambda x: x['percentage'], reverse=True))])
                section_df.to_excel(writer, index=False, sheet_name=sheet_name)

        output.seek(0)
        st.download_button(
            label="📥 Download Excel",
            data=output,
            file_name=f"Collected_Grades_{course_data.get('course_code', '')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )

    with col2:
        # PDF Export
        if PDF_AVAILABLE:
            pdf_data = generate_collected_grades_pdf(
                course_data, selected_sections, sections_reports, collected_stats, program_data
            )
            if pdf_data:
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_data,
                    file_name=f"Collected_Grades_{course_data.get('course_code', '')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="secondary"
                )
        else:
            st.warning("PDF export requires reportlab. Install with: pip install reportlab")

    with col3:
        st.info(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

"""
تقرير ورقة النشاط التقييمي
Activity Sheet Report
"""

import streamlit as st
import pandas as pd
import json
import base64
from pathlib import Path
from datetime import datetime
from io import BytesIO
from models.database import Database, UserRole
from utils.permissions import get_permissions_helper

# PDF generation imports
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import cm, inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


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


def load_topics_data():
    """Load topics data"""
    topics_file = Path(__file__).parent.parent / 'data' / 'course_topics.json'
    if topics_file.exists():
        try:
            with open(topics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"topics": []}
    return {"topics": []}


def load_report_header():
    """Load report header data"""
    header_file = Path(__file__).parent.parent / 'data' / 'report_header.json'
    if header_file.exists():
        try:
            with open(header_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def get_logo_base64():
    """Get logo image as base64 string for HTML display"""
    logo_path = Path(__file__).parent.parent / 'data' / 'images' / 'logo_UTlogo.jfif'
    if logo_path.exists():
        try:
            with open(logo_path, 'rb') as f:
                logo_data = f.read()
                return base64.b64encode(logo_data).decode('utf-8')
        except:
            return None
    return None


def get_course_data(course_id):
    """Get course data"""
    courses_data = load_courses_data()
    for course in courses_data.get('courses', []):
        if course.get('course_id') == course_id:
            return course
    return {}


def get_course_clos(course_id):
    """Get CLOs for a course"""
    clos_data = load_clos_data()
    clos = [clo for clo in clos_data.get('clos', []) if clo.get('course_id') == course_id]
    return sorted(clos, key=lambda x: x.get('clo_code', ''))


def get_course_topics(course_id):
    """Get topics for a course"""
    topics_data = load_topics_data()
    topics = [t for t in topics_data.get('topics', []) if t.get('course_id') == course_id]
    return sorted(topics, key=lambda x: int(x.get('topic_number', 0)))


def get_course_activities(course_id):
    """Get assessment activities for a course"""
    course_data = get_course_data(course_id)
    return course_data.get('assessment_activities', [])


def get_clos_activities_distribution(course_id):
    """Get CLOs-Activities distribution"""
    course_data = get_course_data(course_id)
    return course_data.get('clos_activities_distribution', {})


def get_topics_activities_distribution(course_id):
    """Get Topics-Activities distribution"""
    course_data = get_course_data(course_id)
    return course_data.get('topics_activities_distribution', {})


def get_specifications_table_data(course_id):
    """Get Specifications Table Data (contains exact marks for topic-CLO-activity combinations)"""
    course_data = get_course_data(course_id)
    return course_data.get('specifications_table_data', {})


def calculate_activity_sheet_data(course_id, activity_name):
    """Calculate the activity sheet data showing topics vs CLOs for a specific activity
    Uses specifications_table_data for accurate marks retrieval
    """
    topics = get_course_topics(course_id)
    clos = get_course_clos(course_id)
    clos_activities_dist = get_clos_activities_distribution(course_id)
    specifications_data = get_specifications_table_data(course_id)

    if not topics or not clos:
        return None, None, None, None

    # Get CLO codes that have marks in this activity (filter out CLOs with 0 marks)
    activity_clo_marks = clos_activities_dist.get(activity_name, {})
    active_clos = [clo for clo in clos if activity_clo_marks.get(clo.get('clo_code'), 0) > 0]

    # If no CLOs have marks in this activity, return empty
    if not active_clos:
        return [], [], {}, 0

    # Build the matrix: topics (rows) x CLOs (columns)
    # Use specifications_table_data for accurate marks
    matrix_data = []
    clo_totals = {clo.get('clo_code'): 0 for clo in active_clos}

    for topic in topics:
        topic_id = topic.get('topic_id')
        topic_number = topic.get('topic_number', '')
        topic_title = topic.get('topic_title', '')

        # Get specifications data for this topic
        topic_specs = specifications_data.get(topic_id, {})

        row_data = {
            'topic_number': topic_number,
            'topic_title': topic_title,
            'clo_marks': {}
        }

        row_total = 0
        for clo in active_clos:
            clo_code = clo.get('clo_code')
            # Get mark from specifications_table_data using key format: {CLO_code}_{Activity_name}
            spec_key = f"{clo_code}_{activity_name}"
            activity_mark = topic_specs.get(spec_key, 0)

            row_data['clo_marks'][clo_code] = round(activity_mark, 1) if activity_mark else 0
            row_total += activity_mark
            clo_totals[clo_code] += activity_mark

        row_data['row_total'] = round(row_total, 1)

        # Only include topics that have marks in this activity (filter out topics with 0 marks)
        if row_total > 0:
            matrix_data.append(row_data)

    # Calculate grand total
    grand_total = sum(clo_totals.values())

    return matrix_data, active_clos, clo_totals, grand_total


def generate_activity_sheet_pdf(course_data, activity_name, matrix_data, active_clos, clo_totals, grand_total, header_data):
    """Generate PDF for Activity Sheet"""
    if not PDF_AVAILABLE:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=1*cm, leftMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=18, spaceAfter=10, textColor=colors.HexColor('#1565c0'))
    header_style_en = ParagraphStyle('HeaderEN', parent=styles['Normal'], alignment=TA_LEFT, fontSize=11)
    header_style_ar = ParagraphStyle('HeaderAR', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=11)
    center_style = ParagraphStyle('Center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)

    elements = []

    # ===== UNIVERSITY HEADER =====
    # Load logo for PDF
    logo_path = Path(__file__).parent.parent / 'data' / 'images' / 'logo_UTlogo.jfif'
    logo_element = ""
    if logo_path.exists():
        try:
            logo_element = Image(str(logo_path), width=2*cm, height=2*cm)
        except:
            logo_element = ""

    # Create a 3-column header: English | Logo | Arabic
    header_table_data = [[
        Paragraph(f"{header_data.get('university_name_en', 'University')}<br/>{header_data.get('faculty_name_en', 'Faculty')}<br/>{header_data.get('department_name_en', 'Department')}", header_style_en),
        logo_element,
        Paragraph(f"{header_data.get('university_name_ar', 'الجامعة')}<br/>{header_data.get('faculty_name_ar', 'الكلية')}<br/>{header_data.get('department_name_ar', 'القسم')}", header_style_ar)
    ]]

    header_table = Table(header_table_data, colWidths=[8*cm, 8*cm, 8*cm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))

    # Horizontal line
    line_data = [[""]]
    line_table = Table(line_data, colWidths=[26*cm])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#1565c0')),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 0.2*inch))

    # ===== TITLE =====
    title_text = f"{activity_name} Sheet - {course_data.get('course_code', '')}"
    elements.append(Paragraph(title_text, title_style))
    elements.append(Spacer(1, 0.1*inch))

    # Course info
    course_info = f"Course: {course_data.get('course_title_en', '')} | Total Marks: {grand_total:.1f}"
    elements.append(Paragraph(course_info, center_style))
    elements.append(Spacer(1, 0.3*inch))

    # ===== ACTIVITY SHEET TABLE =====
    # Build table headers
    clo_codes = [clo.get('clo_code') for clo in active_clos]
    table_headers = ['No', 'List of Topics'] + clo_codes + ['Total']

    # Build table data
    table_data = [table_headers]

    for i, row in enumerate(matrix_data, 1):
        row_values = [str(i), row['topic_title'][:50] + '...' if len(row['topic_title']) > 50 else row['topic_title']]
        for clo_code in clo_codes:
            mark = row['clo_marks'].get(clo_code, 0)
            row_values.append(f"{mark:.1f}" if mark > 0 else "")
        row_values.append(f"{row['row_total']:.1f}" if row['row_total'] > 0 else "")
        table_data.append(row_values)

    # Add totals row
    totals_row = ['', 'Total']
    for clo_code in clo_codes:
        total = clo_totals.get(clo_code, 0)
        totals_row.append(f"{total:.1f}" if total > 0 else "")
    totals_row.append(f"{grand_total:.1f}")
    table_data.append(totals_row)

    # Calculate column widths
    num_clos = len(clo_codes)
    no_width = 1*cm
    topic_width = 6*cm
    total_width = 1.5*cm
    remaining_width = 26*cm - no_width - topic_width - total_width
    clo_width = remaining_width / num_clos if num_clos > 0 else 2*cm

    col_widths = [no_width, topic_width] + [clo_width] * num_clos + [total_width]

    activity_table = Table(table_data, colWidths=col_widths)

    # Table styling
    table_style = [
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c8e6c9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        # CLOs header row (second level)
        ('BACKGROUND', (2, 0), (-2, 0), colors.HexColor('#a5d6a7')),

        # Total row
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c8e6c9')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),

        # All cells
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # No column
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),    # Topics column
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'), # CLO columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),

        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f5f5f5')]),
    ]

    activity_table.setStyle(TableStyle(table_style))
    elements.append(activity_table)

    # Footer
    elements.append(Spacer(1, 0.3*inch))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, textColor=colors.HexColor('#999999'))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | CLO Measurement System", footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def show_activity_sheet_report(db: Database, user, lang: str):
    """Display Activity Sheet Report page"""

    st.title("📝 Activity Sheet Report")
    st.caption("Generate assessment activity sheets showing topics vs CLOs distribution")

    # Initialize permissions helper
    perm = get_permissions_helper(db, user)

    # Load data and apply permissions filtering
    programs_data = load_programs_data()
    all_programs = programs_data.get('programs', [])
    programs = perm.filter_programs(all_programs)

    courses_data = load_courses_data()
    all_courses = courses_data.get('courses', [])
    courses = perm.filter_courses(all_courses)
    header_data = load_report_header()

    # Selection Filters
    st.markdown("### Select Course and Activity")

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
            "Program / البرنامج",
            program_options,
            key="activity_sheet_program_filter"
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
                "Course / المقرر",
                course_options,
                key="activity_sheet_course_filter"
            )

            selected_course_id = None
            if selected_course_display != "-- Select Course --":
                selected_course_id = course_map.get(selected_course_display)
        else:
            st.selectbox(
                "Course / المقرر",
                ["-- Select Program First --"],
                disabled=True,
                key="activity_sheet_course_filter_disabled"
            )
            selected_course_id = None

    if not selected_course_id:
        st.info("Please select a Program and Course to view available activities")
        return

    # Get course data
    course_data = get_course_data(selected_course_id)

    # Course Version Display
    current_version = course_data.get('course_version', '1')
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 10px 20px; border-radius: 8px; margin: 10px 0; display: inline-block;">
        <span style="color: white; font-size: 14px;">
            📚 Course Version: <strong>{current_version}</strong>
        </span>
    </div>
    """, unsafe_allow_html=True)

    activities = get_course_activities(selected_course_id)
    topics = get_course_topics(selected_course_id)
    clos = get_course_clos(selected_course_id)

    if not activities:
        st.warning("No assessment activities defined for this course. Please complete Stage 1 first.")
        return

    if not topics:
        st.warning("No topics defined for this course. Please add course topics first.")
        return

    if not clos:
        st.warning("No CLOs defined for this course. Please add CLOs first.")
        return

    # Activity Selection
    st.markdown("### Select Activity Type / اختر نوع النشاط")

    activity_names = [a.get('assessment_task') for a in activities]
    selected_activity = st.selectbox(
        "Assessment Activity / نشاط التقييم",
        activity_names,
        key="activity_sheet_activity_select"
    )

    if not selected_activity:
        return

    # Get activity details
    activity_details = None
    for a in activities:
        if a.get('assessment_task') == selected_activity:
            activity_details = a
            break

    # Calculate activity sheet data
    result = calculate_activity_sheet_data(selected_course_id, selected_activity)

    if result[0] is None:
        st.warning("Could not generate activity sheet. Please ensure topics and CLOs are properly configured.")
        return

    matrix_data, active_clos, clo_totals, grand_total = result

    # Check if there are any topics or CLOs included in this activity
    if not active_clos:
        st.warning(f"No CLOs are assigned to the '{selected_activity}' activity. Please configure CLO distribution for this activity first.")
        return

    if not matrix_data:
        st.warning(f"No topics are assigned to the '{selected_activity}' activity. Please configure topic distribution for this activity first.")
        return

    # ===============================
    # Display Activity Sheet
    # ===============================
    st.markdown("---")

    # Get logo for header
    logo_base64 = get_logo_base64()
    logo_html = f'<img src="data:image/jpeg;base64,{logo_base64}" style="height: 80px; width: auto;">' if logo_base64 else ''

    # Header
    header_html = f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <div style="text-align: left; flex: 1;">
                <p style="margin: 2px 0; font-size: 14px;">{header_data.get('university_name_en', 'University')}</p>
                <p style="margin: 2px 0; font-size: 14px;">{header_data.get('faculty_name_en', 'Faculty')}</p>
                <p style="margin: 2px 0; font-size: 14px;">{header_data.get('department_name_en', 'Department')}</p>
            </div>
            <div style="text-align: center; flex: 1;">
                {logo_html}
            </div>
            <div style="text-align: right; flex: 1;">
                <p style="margin: 2px 0; font-size: 14px;">{header_data.get('university_name_ar', 'الجامعة')}</p>
                <p style="margin: 2px 0; font-size: 14px;">{header_data.get('faculty_name_ar', 'الكلية')}</p>
                <p style="margin: 2px 0; font-size: 14px;">{header_data.get('department_name_ar', 'القسم')}</p>
            </div>
        </div>
        <hr style="border: 2px solid #1565c0; margin: 10px 0;">
        <h2 style="color: #1565c0; margin: 15px 0;">{selected_activity} Sheet - {course_data.get('course_code', '')}</h2>
        <p style="color: #666; margin: 5px 0;">
            Course: {course_data.get('course_title_en', '')} |
            Activity Weight: {activity_details.get('percentage', 0)}% |
            Total Marks: {grand_total:.1f}
        </p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # Build DataFrame for display
    clo_codes = [clo.get('clo_code') for clo in active_clos]

    # Create table data
    table_rows = []
    for i, row in enumerate(matrix_data, 1):
        row_dict = {
            'No': i,
            'List of Topics': row['topic_title']
        }
        for clo_code in clo_codes:
            mark = row['clo_marks'].get(clo_code, 0)
            row_dict[clo_code] = mark if mark > 0 else None
        row_dict['Total'] = row['row_total'] if row['row_total'] > 0 else None
        table_rows.append(row_dict)

    # Add totals row
    totals_row = {'No': '', 'List of Topics': 'Total'}
    for clo_code in clo_codes:
        totals_row[clo_code] = round(clo_totals.get(clo_code, 0), 1) if clo_totals.get(clo_code, 0) > 0 else None
    totals_row['Total'] = round(grand_total, 1)
    table_rows.append(totals_row)

    df = pd.DataFrame(table_rows)

    # Display table with styling
    st.markdown("### 📊 Activity Sheet Table / جدول ورقة النشاط")

    # Apply styling
    def style_table(val):
        if pd.isna(val) or val == '' or val is None:
            return 'background-color: white'
        return ''

    styled_df = df.style.applymap(style_table)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Summary Statistics
    st.markdown("---")
    st.markdown("### 📈 Summary / ملخص")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 15px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Total Topics</p>
            <p style="color: white; margin: 0; font-size: 28px; font-weight: bold;">{len(matrix_data)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                    padding: 15px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Active CLOs</p>
            <p style="color: white; margin: 0; font-size: 28px; font-weight: bold;">{len(active_clos)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 15px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Activity Weight</p>
            <p style="color: white; margin: 0; font-size: 28px; font-weight: bold;">{activity_details.get('percentage', 0)}%</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    padding: 15px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Total Marks</p>
            <p style="color: white; margin: 0; font-size: 28px; font-weight: bold;">{grand_total:.1f}</p>
        </div>
        """, unsafe_allow_html=True)

    # CLO Distribution for this activity
    st.markdown("### 📊 CLO Distribution for This Activity")

    clo_dist_data = []
    for clo in active_clos:
        clo_code = clo.get('clo_code')
        clo_desc = clo.get('clo_description', '')[:50]
        clo_domain = clo.get('domain', '')
        clo_total = clo_totals.get(clo_code, 0)

        clo_dist_data.append({
            'CLO Code': clo_code,
            'Domain': clo_domain,
            'Description': clo_desc + '...' if len(clo.get('clo_description', '')) > 50 else clo_desc,
            'Marks': round(clo_total, 1)
        })

    clo_df = pd.DataFrame(clo_dist_data)
    st.dataframe(clo_df, use_container_width=True, hide_index=True)

    # ===============================
    # Export Options
    # ===============================
    st.markdown("---")
    st.markdown("### 💾 Export Report / تصدير التقرير")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Excel Export
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Activity Sheet
            df.to_excel(writer, index=False, sheet_name='Activity Sheet')

            # CLO Distribution
            clo_df.to_excel(writer, index=False, sheet_name='CLO Distribution')

            # Summary
            summary_df = pd.DataFrame([{
                'Course': f"{course_data.get('course_code', '')} - {course_data.get('course_title_en', '')}",
                'Activity': selected_activity,
                'Activity Weight': f"{activity_details.get('percentage', 0)}%",
                'Total Marks': grand_total,
                'Total Topics': len(matrix_data),
                'Active CLOs': len(active_clos)
            }])
            summary_df.to_excel(writer, index=False, sheet_name='Summary')

        output.seek(0)

        st.download_button(
            label="📥 Download Excel",
            data=output,
            file_name=f"Activity_Sheet_{course_data.get('course_code', '')}_{selected_activity.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )

    with col2:
        # PDF Export
        if PDF_AVAILABLE:
            pdf_data = generate_activity_sheet_pdf(
                course_data, selected_activity, matrix_data, active_clos, clo_totals, grand_total, header_data
            )
            if pdf_data:
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_data,
                    file_name=f"Activity_Sheet_{course_data.get('course_code', '')}_{selected_activity.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="secondary"
                )
        else:
            st.warning("PDF export requires reportlab")

    with col3:
        st.info(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

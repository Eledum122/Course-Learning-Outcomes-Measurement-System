"""
لوحة بيانات درجات الطلاب
Student Grades Dashboard
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from models.database import Database, UserRole
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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


def show_grades_dashboard(db: Database, user, lang: str):
    """Display Student Grades Dashboard"""

    st.title("📊 Student Grades Dashboard / لوحة بيانات الدرجات")
    st.caption("Comprehensive analysis of student performance and grade distribution")

    # Load sections
    sections_data = load_sections_data()
    sections = sections_data.get('sections', [])

    if not sections:
        st.warning("No sections found. Please create sections first.")
        return

    # Section Selection
    st.markdown("### Select Section / اختر الشعبة")

    col1, col2 = st.columns([2, 1])

    with col1:
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

        selected_section_display = st.selectbox("Section / الشعبة", section_options, key="dashboard_section_select")

        selected_section = None
        if selected_section_display != "-- Select Section --":
            selected_section = section_map.get(selected_section_display)

    if not selected_section:
        st.info("Please select a section to view the dashboard")
        return

    section_id = selected_section.get('section_id')
    course_id = selected_section.get('course_id')

    # Get data
    section_students = get_section_students(section_id)
    course_data = get_course_data(course_id)
    clos_distribution = get_clos_activities_distribution(course_id)
    grades = get_section_grades(section_id)

    # Count students by status
    total_all_students = len(section_students)
    regular_students = [s for s in section_students if s.get('status') == 'Regular']
    excused_students = [s for s in section_students if s.get('status') == 'Excused']  # معتذر
    denied_students = [s for s in section_students if s.get('status') == 'Denied']    # محروم
    incomplete_students = [s for s in section_students if s.get('status') == 'Incomplete']  # غير مكمل

    regular_count = len(regular_students)
    excused_count = len(excused_students)
    denied_count = len(denied_students)
    incomplete_count = len(incomplete_students)

    if not regular_students:
        st.warning("No regular students in this section.")
        return

    if not clos_distribution:
        st.warning("CLOs distribution not defined. Please complete Stage 2.4 first.")
        return

    if not grades:
        st.warning("No grades entered for this section. Please enter grades first.")
        return

    # Calculate max total
    max_total = calculate_max_total(clos_distribution)

    # Calculate student results
    student_results = []
    for student in regular_students:
        student_id = student.get('student_record_id')
        total_marks = calculate_student_total(student_id, grades, clos_distribution)
        percentage = (total_marks / max_total * 100) if max_total > 0 else 0
        grade_info = get_grade_info(percentage)

        student_results.append({
            'student_no': student.get('student_no'),
            'student_name': student.get('student_name'),
            'total_marks': total_marks,
            'max_marks': max_total,
            'percentage': percentage,
            'grade': grade_info['grade'],
            'grade_code': grade_info['code'],
            'color': grade_info['color']
        })

    # Convert to DataFrame
    df = pd.DataFrame(student_results)

    st.markdown("---")

    # ===============================
    # Dashboard Header
    # ===============================
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 25px; border-radius: 15px; margin-bottom: 25px; text-align: center;">
        <h2 style="color: white; margin: 0;">📊 Student Performance Dashboard</h2>
        <h3 style="color: #e0e0e0; margin: 10px 0;">لوحة بيانات أداء الطلاب</h3>
        <p style="color: #e8e8e8; margin: 5px 0; font-size: 16px;">
            {course_data.get('course_code', '')} - {course_data.get('course_title_en', '')}
        </p>
        <p style="color: #d0d0d0; margin: 5px 0;">
            Section: {selected_section.get('section_number')} |
            Semester: {selected_section.get('semester_code')} {selected_section.get('academic_year')} |
            Students: {len(regular_students)}
        </p>
    </div>
    """, unsafe_allow_html=True)

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
            <p style="color: white; margin: 0; font-size: 36px; font-weight: bold; line-height: 1.2;">{total_all_students}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Regular / منتظم</p>
            <p style="color: white; margin: 0; font-size: 36px; font-weight: bold; line-height: 1.2;">{regular_count}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Excused / معتذر</p>
            <p style="color: white; margin: 0; font-size: 36px; font-weight: bold; line-height: 1.2;">{excused_count}</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Denied / محروم</p>
            <p style="color: white; margin: 0; font-size: 36px; font-weight: bold; line-height: 1.2;">{denied_count}</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Incomplete / غير مكمل</p>
            <p style="color: white; margin: 0; font-size: 36px; font-weight: bold; line-height: 1.2;">{incomplete_count}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ===============================
    # Key Statistics Cards
    # ===============================
    st.markdown("### 📈 Key Statistics / الإحصائيات الرئيسية")

    # Calculate statistics
    percentages = df['percentage'].tolist()
    mean_pct = sum(percentages) / len(percentages) if percentages else 0
    sorted_pct = sorted(percentages)
    n = len(sorted_pct)
    median_pct = sorted_pct[n // 2] if n % 2 == 1 else (sorted_pct[n // 2 - 1] + sorted_pct[n // 2]) / 2 if n > 0 else 0
    min_pct = min(percentages) if percentages else 0
    max_pct = max(percentages) if percentages else 0

    # Standard deviation
    if len(percentages) > 1:
        variance = sum((x - mean_pct) ** 2 for x in percentages) / len(percentages)
        std_pct = variance ** 0.5
    else:
        std_pct = 0

    # Pass/Fail counts
    pass_count = sum(1 for p in percentages if p >= 60)
    fail_count = len(percentages) - pass_count
    pass_rate = (pass_count / len(percentages) * 100) if percentages else 0

    # Display stats in cards
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Mean / المتوسط</p>
            <p style="color: white; margin: 0; font-size: 28px; font-weight: bold; line-height: 1.2;">{mean_pct:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Median / الوسيط</p>
            <p style="color: white; margin: 0; font-size: 28px; font-weight: bold; line-height: 1.2;">{median_pct:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Std Dev / الانحراف</p>
            <p style="color: white; margin: 0; font-size: 28px; font-weight: bold; line-height: 1.2;">{std_pct:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Min / أدنى</p>
            <p style="color: white; margin: 0; font-size: 28px; font-weight: bold; line-height: 1.2;">{min_pct:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">Max / أعلى</p>
            <p style="color: white; margin: 0; font-size: 28px; font-weight: bold; line-height: 1.2;">{max_pct:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                    padding: 12px; border-radius: 12px; text-align: center;">
            <p style="color: #333; margin: 0; font-size: 12px;">Pass Rate / نسبة النجاح</p>
            <p style="color: #333; margin: 0; font-size: 28px; font-weight: bold; line-height: 1.2;">{pass_rate:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ===============================
    # Charts Section
    # ===============================
    st.markdown("### 📊 Visual Analytics / التحليل البصري")

    # Row 1: Grade Distribution and Pass/Fail Pie
    col1, col2 = st.columns([2, 1])

    with col1:
        # Grade Distribution Bar Chart
        grade_counts = df['grade_code'].value_counts().reindex(
            [g['code'] for g in GRADE_SCALE], fill_value=0
        )

        fig_bar = go.Figure(data=[
            go.Bar(
                x=grade_counts.index,
                y=grade_counts.values,
                marker_color=[g['color'] for g in GRADE_SCALE],
                text=grade_counts.values,
                textposition='outside',
                textfont=dict(size=14, color='white')
            )
        ])

        fig_bar.update_layout(
            title=dict(
                text="Grade Distribution / توزيع الدرجات",
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
                values=[pass_count, fail_count],
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

    # Row 2: Histogram and Box Plot
    col1, col2 = st.columns(2)

    with col1:
        # Histogram of Percentages
        fig_hist = go.Figure(data=[
            go.Histogram(
                x=df['percentage'],
                nbinsx=10,
                marker_color='#667eea',
                marker_line_color='white',
                marker_line_width=1,
                opacity=0.8
            )
        ])

        # Add mean line
        fig_hist.add_vline(
            x=mean_pct,
            line_dash="dash",
            line_color="#ff6b6b",
            annotation_text=f"Mean: {mean_pct:.1f}%",
            annotation_position="top"
        )

        fig_hist.update_layout(
            title=dict(
                text="Score Distribution / توزيع النتائج",
                font=dict(size=18, color='white'),
                x=0.5
            ),
            xaxis_title="Percentage (%)",
            yaxis_title="Frequency",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.2)'),
            height=350
        )

        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        # Box Plot
        fig_box = go.Figure(data=[
            go.Box(
                y=df['percentage'],
                marker_color='#764ba2',
                boxmean='sd',
                name='Scores',
                fillcolor='rgba(118, 75, 162, 0.5)',
                line=dict(color='#764ba2')
            )
        ])

        fig_box.update_layout(
            title=dict(
                text="Score Statistics / إحصائيات النتائج",
                font=dict(size=18, color='white'),
                x=0.5
            ),
            yaxis_title="Percentage (%)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.2)'),
            height=350
        )

        st.plotly_chart(fig_box, use_container_width=True)

    # Row 3: Detailed Grade Breakdown
    st.markdown("### 📋 Grade Breakdown / تفصيل الدرجات")

    # Create grade breakdown table
    grade_breakdown = []
    for grade in GRADE_SCALE:
        count = len(df[df['grade_code'] == grade['code']])
        pct = (count / len(df) * 100) if len(df) > 0 else 0
        grade_breakdown.append({
            'Percentage Range': f"{grade['min']}% - {grade['max']}%",
            'Grade': grade['grade'],
            'Grade Code': grade['code'],
            'Students': count,
            'Percentage': f"{pct:.1f}%"
        })

    df_breakdown = pd.DataFrame(grade_breakdown)

    # Display as styled table
    col1, col2 = st.columns([2, 1])

    with col1:
        # Horizontal bar chart for grade counts
        fig_hbar = go.Figure(data=[
            go.Bar(
                y=[f"{g['code']} - {g['grade']}" for g in GRADE_SCALE],
                x=[len(df[df['grade_code'] == g['code']]) for g in GRADE_SCALE],
                orientation='h',
                marker_color=[g['color'] for g in GRADE_SCALE],
                text=[len(df[df['grade_code'] == g['code']]) for g in GRADE_SCALE],
                textposition='outside',
                textfont=dict(size=12, color='white')
            )
        ])

        fig_hbar.update_layout(
            title=dict(
                text="Students per Grade / الطلاب حسب التقدير",
                font=dict(size=18, color='white'),
                x=0.5
            ),
            xaxis_title="Number of Students",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.2)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            height=400
        )

        st.plotly_chart(fig_hbar, use_container_width=True)

    with col2:
        st.markdown("#### Grade Scale / سلم الدرجات")
        for grade in GRADE_SCALE:
            count = len(df[df['grade_code'] == grade['code']])
            st.markdown(f"""
            <div style="display:flex;align-items:center;margin:5px 0;padding:8px;
                        background:{grade['color']};border-radius:8px;">
                <span style="color:white;font-weight:bold;width:40px;">{grade['code']}</span>
                <span style="color:white;flex:1;">{grade['grade']}</span>
                <span style="color:white;font-weight:bold;width:30px;text-align:right;">{count}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ===============================
    # Student Results Table
    # ===============================
    st.markdown("### 📝 Student Results / نتائج الطلاب")

    # Sort by percentage descending
    df_display = df.sort_values('percentage', ascending=False).reset_index(drop=True)
    df_display.index = df_display.index + 1  # Start from 1

    # Format for display
    df_display['Rank'] = range(1, len(df_display) + 1)
    df_display = df_display[['Rank', 'student_no', 'student_name', 'total_marks', 'percentage', 'grade_code', 'grade']]
    df_display.columns = ['Rank', 'Student No', 'Student Name', 'Total Marks', 'Percentage', 'Grade', 'Grade Name']
    df_display['Percentage'] = df_display['Percentage'].apply(lambda x: f"{x:.1f}%")
    df_display['Total Marks'] = df_display['Total Marks'].apply(lambda x: f"{x:.1f}/{max_total}")

    st.dataframe(df_display, use_container_width=True, height=400)

    st.markdown("---")

    # ===============================
    # Export Options
    # ===============================
    st.markdown("### 💾 Export Report / تصدير التقرير")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Export to Excel
        from io import BytesIO
        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Student results
            df_export = df[['student_no', 'student_name', 'total_marks', 'percentage', 'grade_code', 'grade']]
            df_export.columns = ['Student No', 'Student Name', 'Total Marks', 'Percentage', 'Grade Code', 'Grade']
            df_export.to_excel(writer, index=False, sheet_name='Student Results')

            # Statistics summary
            stats_df = pd.DataFrame({
                'Statistic': ['Mean', 'Median', 'Std Deviation', 'Min', 'Max', 'Pass Count', 'Fail Count', 'Pass Rate'],
                'Value': [f"{mean_pct:.2f}%", f"{median_pct:.2f}%", f"{std_pct:.2f}%",
                         f"{min_pct:.2f}%", f"{max_pct:.2f}%", pass_count, fail_count, f"{pass_rate:.2f}%"]
            })
            stats_df.to_excel(writer, index=False, sheet_name='Statistics')

            # Grade breakdown
            df_breakdown.to_excel(writer, index=False, sheet_name='Grade Breakdown')

        output.seek(0)

        st.download_button(
            label="📥 Excel تحميل",
            data=output,
            file_name=f"Grades_Dashboard_{course_data.get('course_code', '')}_{selected_section.get('section_number')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )

    with col2:
        # Generate PDF Report
        def generate_pdf_report():
            """Generate PDF report with all dashboard data"""
            from io import BytesIO
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, cm
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1*cm, leftMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=18, spaceAfter=20)
            subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'], alignment=TA_CENTER, fontSize=14, spaceAfter=10)
            section_style = ParagraphStyle('Section', parent=styles['Heading3'], fontSize=12, spaceAfter=10, spaceBefore=15)

            elements = []

            # Title
            elements.append(Paragraph("Student Grades Dashboard", title_style))
            elements.append(Paragraph("لوحة بيانات درجات الطلاب", subtitle_style))
            elements.append(Spacer(1, 0.3*inch))

            # Course Info
            course_info = f"""
            <b>Course:</b> {course_data.get('course_code', '')} - {course_data.get('course_title_en', '')}<br/>
            <b>Section:</b> {selected_section.get('section_number')}<br/>
            <b>Semester:</b> {selected_section.get('semester_code')} {selected_section.get('academic_year')}<br/>
            <b>Report Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """
            elements.append(Paragraph(course_info, styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))

            # Student Status Table
            elements.append(Paragraph("Student Status / حالة الطلاب", section_style))
            status_data = [
                ['Total', 'Regular', 'Excused', 'Denied', 'Incomplete'],
                [str(total_all_students), str(regular_count), str(excused_count), str(denied_count), str(incomplete_count)]
            ]
            status_table = Table(status_data, colWidths=[3*cm]*5)
            status_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(status_table)
            elements.append(Spacer(1, 0.3*inch))

            # Statistics Table
            elements.append(Paragraph("Key Statistics / الإحصائيات الرئيسية", section_style))
            stats_data = [
                ['Mean', 'Median', 'Std Dev', 'Min', 'Max', 'Pass Rate'],
                [f"{mean_pct:.1f}%", f"{median_pct:.1f}%", f"{std_pct:.1f}%", f"{min_pct:.1f}%", f"{max_pct:.1f}%", f"{pass_rate:.1f}%"]
            ]
            stats_table = Table(stats_data, colWidths=[2.5*cm]*6)
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(stats_table)
            elements.append(Spacer(1, 0.3*inch))

            # Grade Breakdown Table
            elements.append(Paragraph("Grade Breakdown / توزيع الدرجات", section_style))
            grade_data = [['Grade', 'Code', 'Range', 'Count', '%']]
            for grade in GRADE_SCALE:
                count = len(df[df['grade_code'] == grade['code']])
                pct = (count / len(df) * 100) if len(df) > 0 else 0
                grade_data.append([grade['grade'], grade['code'], f"{grade['min']}-{grade['max']}%", str(count), f"{pct:.1f}%"])

            grade_table = Table(grade_data, colWidths=[4*cm, 1.5*cm, 3*cm, 2*cm, 2*cm])
            grade_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ]))
            elements.append(grade_table)
            elements.append(Spacer(1, 0.3*inch))

            # Student Results Table
            elements.append(Paragraph("Student Results / نتائج الطلاب", section_style))
            results_data = [['#', 'Student No', 'Name', 'Marks', '%', 'Grade']]
            sorted_df = df.sort_values('percentage', ascending=False)
            for i, (_, row) in enumerate(sorted_df.iterrows(), 1):
                results_data.append([
                    str(i),
                    row['student_no'],
                    row['student_name'][:20] + '...' if len(str(row['student_name'])) > 20 else row['student_name'],
                    f"{row['total_marks']:.1f}",
                    f"{row['percentage']:.1f}%",
                    row['grade_code']
                ])

            results_table = Table(results_data, colWidths=[1*cm, 2.5*cm, 5*cm, 2*cm, 2*cm, 1.5*cm])
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ]))
            elements.append(results_table)

            doc.build(elements)
            buffer.seek(0)
            return buffer.getvalue()

        try:
            pdf_data = generate_pdf_report()
            st.download_button(
                label="📄 PDF تحميل",
                data=pdf_data,
                file_name=f"Grades_Dashboard_{course_data.get('course_code', '')}_{selected_section.get('section_number')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="secondary"
            )
        except ImportError:
            st.warning("PDF export requires reportlab. Install with: pip install reportlab")

    with col3:
        st.info(f"📅 Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

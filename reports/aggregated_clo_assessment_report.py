"""
تقرير قياس نواتج تعلم المقرر المجمع
Aggregated CLO Assessment Report
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import List
from datetime import datetime
import os
from models import Course, CourseSection
from utils.report_utils import add_report_header, add_page_number_first, add_page_number_with_watermark


class AggregatedCLOAssessmentReport:
    """تقرير قياس نواتج تعلم المقرر المجمع"""

    def __init__(self, course: Course, sections: List[CourseSection], language: str = 'en'):
        """
        تهيئة مولد التقرير

        Args:
            course: المقرر الدراسي
            sections: قائمة الشعب المختارة
            language: اللغة (ar/en)
        """
        self.course = course
        self.sections = sections
        self.language = language
        self.is_rtl = language == 'ar'

        # تسجيل الخطوط العربية
        if self.is_rtl:
            font_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'Amiri-Regular.ttf')
            font_bold_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'Amiri-Bold.ttf')

            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Amiri', font_path))
            if os.path.exists(font_bold_path):
                pdfmetrics.registerFont(TTFont('Amiri-Bold', font_bold_path))

        # إنشاء الأنماط
        self.styles = self._create_styles()

    def _create_styles(self):
        """إنشاء أنماط التنسيق"""
        styles = getSampleStyleSheet()

        if self.is_rtl:
            # أنماط عربية
            styles.add(ParagraphStyle(
                name='ArabicTitle',
                fontName='Amiri-Bold',
                fontSize=16,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#1976D2'),
                spaceAfter=12
            ))

            styles.add(ParagraphStyle(
                name='ArabicNormal',
                fontName='Amiri',
                fontSize=11,
                alignment=TA_RIGHT,
                rightIndent=0,
                leftIndent=0
            ))

            styles.add(ParagraphStyle(
                name='ArabicHeader',
                fontName='Amiri-Bold',
                fontSize=12,
                alignment=TA_CENTER,
                textColor=colors.white
            ))
        else:
            # أنماط إنجليزية
            styles.add(ParagraphStyle(
                name='EnglishTitle',
                fontName='Helvetica-Bold',
                fontSize=16,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#1976D2'),
                spaceAfter=12
            ))

            styles.add(ParagraphStyle(
                name='EnglishNormal',
                fontName='Helvetica',
                fontSize=10,
                alignment=TA_LEFT
            ))

            styles.add(ParagraphStyle(
                name='EnglishHeader',
                fontName='Helvetica-Bold',
                fontSize=11,
                alignment=TA_CENTER,
                textColor=colors.white
            ))

        return styles

    def _reshape_text(self, text):
        """إعادة تشكيل النص العربي"""
        if self.is_rtl:
            try:
                import arabic_reshaper
                from bidi.algorithm import get_display
                reshaped_text = arabic_reshaper.reshape(text)
                return get_display(reshaped_text)
            except ImportError:
                return text
        return text

    def generate_report(self, output_path: str):
        """
        توليد التقرير

        Args:
            output_path: مسار حفظ الملف
        """
        # إنشاء المستند بالاتجاه الأفقي
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,  # هامش عادي
            bottomMargin=1.5*cm
        )

        # إنشاء عناصر التقرير
        elements = []

        # إضافة ترويسة التقرير
        add_report_header(elements, language=self.language, orientation='landscape')

        # الصفحة الأولى: معلومات المقرر
        elements.extend(self._create_course_info_page())
        elements.append(PageBreak())

        # الصفحة الثانية: نتائج الطلاب
        elements.extend(self._create_student_results_page())
        elements.append(PageBreak())

        # فصل الشعب حسب النوع
        male_sections = [s for s in self.sections if s.gender_section == 'Male']
        female_sections = [s for s in self.sections if s.gender_section == 'Female']

        # الصفحة الثالثة: نتائج المخرجات للشعب الذكور
        if male_sections:
            elements.extend(self._create_clo_assessment_page(male_sections, 'Male'))
            elements.append(PageBreak())

        # الصفحة الرابعة: نتائج المخرجات للشعب الإناث
        if female_sections:
            elements.extend(self._create_clo_assessment_page(female_sections, 'Female'))

        # بناء المستند مع أرقام الصفحات والعلامة المائية
        doc.build(elements, onFirstPage=add_page_number_first, onLaterPages=add_page_number_with_watermark)

    def _create_course_info_page(self):
        """إنشاء صفحة معلومات المقرر"""
        elements = []

        # ترتيب الشعب حسب رقم الشعبة
        sorted_sections = sorted(self.sections, key=lambda s: s.section_number)

        # جمع بيانات الشعب
        section_numbers = [s.section_number for s in sorted_sections]

        # استخراج أسماء المدرسين مع الشعبة والنوع
        instructors_data = []  # [(name, section_number, gender), ...]
        for s in sorted_sections:
            # استخدام مدرس الشعبة، أو "N/A" إذا لم يكن موجوداً
            if s.section_instructor:
                name = s.section_instructor.split('(')[0].strip()
            else:
                name = "N/A"

            section_num = s.section_number
            gender = s.gender_section if hasattr(s, 'gender_section') else ''
            instructors_data.append((name, section_num, gender))

        # استخراج منسق المقرر
        coordinator = ""
        for s in self.sections:
            if s.course_coordinator:
                coordinator = s.course_coordinator.split('(')[0].strip()
                break

        # حساب إحصائيات الطلاب لكل شعبة
        sections_data = {}  # {section_number: {'gender': ..., 'regular': ..., 'prohibited': ..., 'dropped': ..., 'incomplete': ..., 'total': ...}}
        for section in sorted_sections:
            regular = len([st for st in section.students if st.status.value == 'Regular'])
            prohibited = len([st for st in section.students if st.status.value == 'Prohibited'])
            dropped = len([st for st in section.students if st.status.value == 'Dropped'])
            incomplete = len([st for st in section.students if st.status.value == 'Incomplete'])
            total = len(section.students)

            sections_data[section.section_number] = {
                'gender': section.gender_section if hasattr(section, 'gender_section') else '',
                'regular': regular,
                'prohibited': prohibited,
                'dropped': dropped,
                'incomplete': incomplete,
                'total': total
            }

        # استخراج السنة والفصل من أول شعبة
        academic_year = self.sections[0].academic_year if self.sections else ""
        semester = self.sections[0].semester.value if self.sections else ""

        # استخراج البرنامج من معلومات المقرر
        program = ""
        if hasattr(self.course.info, 'program') and self.course.info.program:
            program = self.course.info.program

        # إنشاء الجدول الموحد
        table_data = []

        # الصف 1: Course Title & Course Code
        table_data.append(['Course Title:', self.course.info.course_title, 'Course Code:', self.course.info.course_code, '', '', '', ''])

        # الصف 2: Department & Program
        table_data.append(['Department:', self.course.info.department if hasattr(self.course.info, 'department') else '',
                'Program:', program, '', '', '', ''])

        # الصف 3: College
        table_data.append(['College:', self.course.info.faculty if hasattr(self.course.info, 'faculty') else '', '', '', '', '', '', ''])

        # الصف 4: Institution
        table_data.append(['Institution:', 'University of Tabuk', '', '', '', '', '', ''])

        # الصف 5: Academic Year & Semester
        table_data.append(['Academic Year:', academic_year, 'Semester:', semester, '', '', '', ''])

        # الصف 6: Course Coordinator
        table_data.append(['Course Coordinator:', coordinator, '', '', '', '', '', ''])

        # الصف 7: عناوين جدول المدرسين
        instructor_header = ['Course Instructor', 'Section', 'Gender', 'Regular', 'Prohibited', 'Dropped', 'Incomplete', 'Total']
        table_data.append(instructor_header)

        # صفوف المدرسين (جميع الشعب)
        for i, (name, section_num, gender) in enumerate(instructors_data):
            # حساب الإحصائيات لهذه الشعبة
            if section_num in sections_data:
                regular = sections_data[section_num]['regular']
                prohibited = sections_data[section_num]['prohibited']
                dropped = sections_data[section_num]['dropped']
                incomplete = sections_data[section_num]['incomplete']
                total = sections_data[section_num]['total']
            else:
                regular = prohibited = dropped = incomplete = total = 0

            row = [name, str(section_num), gender, str(regular), str(prohibited), str(dropped), str(incomplete), str(total)]
            table_data.append(row)

        # حفظ رقم صف تاريخ التقرير (سيكون بعد صفوف المدرسين)
        # 6 صفوف معلومات + 1 صف عناوين + عدد صفوف المدرسين
        report_date_row_index = 6 + 1 + len(instructors_data)

        # صف تاريخ التقرير
        table_data.append(['Report Date:', datetime.now().strftime('%Y-%m-%d'), '', '', '', '', '', ''])

        # حساب عرض الأعمدة (8 أعمدة)
        available_width = 25 * cm
        col_widths = [4.5*cm, 2*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm]

        # إنشاء الجدول
        table = Table(table_data, colWidths=col_widths)

        # تنسيق الجدول
        style_commands = [
            # الحدود
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#4472C4')),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#4472C4')),

            # ألوان الخلفية - الصفوف العلوية (المعلومات العامة)
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#D9E2F3')),  # Course Title
            ('BACKGROUND', (2, 0), (2, 0), colors.HexColor('#D9E2F3')),  # Course Code
            ('BACKGROUND', (0, 1), (0, 1), colors.HexColor('#D9E2F3')),  # Department
            ('BACKGROUND', (2, 1), (2, 1), colors.HexColor('#D9E2F3')),  # Program
            ('BACKGROUND', (0, 2), (0, 2), colors.HexColor('#D9E2F3')),  # College
            ('BACKGROUND', (0, 3), (0, 3), colors.HexColor('#D9E2F3')),  # Institution
            ('BACKGROUND', (0, 4), (0, 4), colors.HexColor('#D9E2F3')),  # Academic Year
            ('BACKGROUND', (2, 4), (2, 4), colors.HexColor('#D9E2F3')),  # Semester
            ('BACKGROUND', (0, 5), (0, 5), colors.HexColor('#D9E2F3')),  # Course Coordinator

            # صف عناوين المدرسين
            ('BACKGROUND', (0, 6), (7, 6), colors.HexColor('#B4C7E7')),

            # عمود Total - لون مميز للعنوان
            ('BACKGROUND', (7, 6), (7, 6), colors.HexColor('#FFC000')),  # لون ذهبي للعنوان

            # عمود Total - لون مميز للبيانات
            ('BACKGROUND', (7, 7), (7, 6+len(instructors_data)), colors.HexColor('#FFE699')),  # لون أصفر فاتح

            # صف تاريخ التقرير
            ('BACKGROUND', (0, report_date_row_index), (0, report_date_row_index), colors.HexColor('#D9E2F3')),

            # محاذاة النصوص
            ('ALIGN', (0, 0), (0, 5), 'LEFT'),
            ('ALIGN', (1, 0), (1, 5), 'LEFT'),
            ('ALIGN', (2, 0), (2, 5), 'LEFT'),
            ('ALIGN', (3, 0), (3, 5), 'LEFT'),
            ('ALIGN', (0, 6), (7, 6), 'CENTER'),  # عناوين المدرسين
            ('ALIGN', (0, 7), (0, 6+len(instructors_data)), 'LEFT'),   # أسماء المدرسين
            ('ALIGN', (1, 7), (6, 6+len(instructors_data)), 'CENTER'), # البيانات الإحصائية
            ('ALIGN', (7, 7), (7, 6+len(instructors_data)), 'CENTER'), # عمود Total - متوسط
            ('ALIGN', (0, report_date_row_index), (7, report_date_row_index), 'LEFT'),  # تاريخ التقرير
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # الخط
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTNAME', (0, 0), (0, 5), 'Helvetica-Bold'),  # التسميات اليسرى
            ('FONTNAME', (2, 0), (2, 5), 'Helvetica-Bold'),  # التسميات اليمنى
            ('FONTNAME', (0, 6), (7, 6), 'Helvetica-Bold'),  # عناوين المدرسين
            ('FONTNAME', (7, 7), (7, 6+len(instructors_data)), 'Helvetica-Bold'),  # أرقام Total بخط Bold
            ('FONTNAME', (0, report_date_row_index), (0, report_date_row_index), 'Helvetica-Bold'), # تسمية التاريخ
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTSIZE', (7, 7), (7, 6+len(instructors_data)), 10),  # حجم أكبر قليلاً لعمود Total

            # المسافات
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),

            # دمج الخلايا
            ('SPAN', (1, 0), (2, 0)),  # Course Title value (columns 1-2)
            ('SPAN', (3, 0), (7, 0)),  # Course Code value (columns 3-7)
            ('SPAN', (1, 1), (2, 1)),  # Department value (columns 1-2)
            ('SPAN', (3, 1), (7, 1)),  # Program value (columns 3-7)
            ('SPAN', (1, 2), (7, 2)),  # College value
            ('SPAN', (1, 3), (7, 3)),  # Institution value
            ('SPAN', (1, 4), (2, 4)),  # Academic Year value (columns 1-2)
            ('SPAN', (3, 4), (7, 4)),  # Semester value (columns 3-7)
            ('SPAN', (1, 5), (7, 5)),  # Course Coordinator value
            ('SPAN', (1, report_date_row_index), (7, report_date_row_index)),  # Report Date value
        ]

        table.setStyle(TableStyle(style_commands))

        elements.append(table)

        return elements

    def _create_student_results_page(self):
        """إنشاء صفحة نتائج الطلاب"""
        elements = []

        # العنوان
        title = Paragraph("Student Results", self.styles['EnglishTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))

        # فصل البيانات حسب النوع وترتيب
        sorted_sections = sorted(self.sections, key=lambda s: s.section_number)
        male_sections = sorted([s for s in sorted_sections if s.gender_section == 'Male'], key=lambda s: s.section_number)
        female_sections = sorted([s for s in sorted_sections if s.gender_section == 'Female'], key=lambda s: s.section_number)

        # إنشاء بيانات الجدول
        data = []

        # صف العناوين الرئيسي
        header_row1 = ['Gender', 'Section', '', 'Grades', '', '', '', '', '', '', '', '', 'Status Distributions', '']
        data.append(header_row1)

        # صف العناوين الفرعي
        header_row2 = ['', '', '', 'A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F', 'Pass', 'Fail']
        data.append(header_row2)

        span_commands = []
        current_row = 2  # نبدأ من الصف 2 (بعد العناوين)

        # بيانات الذكور
        if male_sections:
            male_start_row = current_row
            for section in male_sections:
                stats = self._calculate_section_statistics([section])

                # صف عدد الطلاب
                data.append(['Male', f'Section {section.section_number}', 'Number of Students'] +
                           [str(stats['grades'][g]) for g in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F']] +
                           [str(stats['pass']), str(stats['fail'])])

                # صف النسبة المئوية
                data.append(['', '', 'Percentage'] +
                           [f"{stats['grades_pct'][g]:.1f}%" for g in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F']] +
                           [f"{stats['pass_pct']:.1f}%", f"{stats['fail_pct']:.1f}%"])

                # دمج Gender و Section للصفين
                span_commands.append(('SPAN', (0, current_row), (0, current_row+1)))  # Gender
                span_commands.append(('SPAN', (1, current_row), (1, current_row+1)))  # Section
                current_row += 2

            # إجمالي الذكور
            male_stats = self._calculate_section_statistics(male_sections)
            data.append(['Total (Male)', '', 'Number of Students'] +
                       [str(male_stats['grades'][g]) for g in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F']] +
                       [str(male_stats['pass']), str(male_stats['fail'])])
            data.append(['', '', 'Percentage'] +
                       [f"{male_stats['grades_pct'][g]:.1f}%" for g in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F']] +
                       [f"{male_stats['pass_pct']:.1f}%", f"{male_stats['fail_pct']:.1f}%"])

            span_commands.append(('SPAN', (0, current_row), (1, current_row)))  # Total Male gender
            span_commands.append(('SPAN', (0, current_row+1), (1, current_row+1)))  # Total Male percentage
            current_row += 2

        # بيانات الإناث
        if female_sections:
            female_start_row = current_row
            for section in female_sections:
                stats = self._calculate_section_statistics([section])

                # صف عدد الطلاب
                data.append(['Female', f'Section {section.section_number}', 'Number of Students'] +
                           [str(stats['grades'][g]) for g in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F']] +
                           [str(stats['pass']), str(stats['fail'])])

                # صف النسبة المئوية
                data.append(['', '', 'Percentage'] +
                           [f"{stats['grades_pct'][g]:.1f}%" for g in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F']] +
                           [f"{stats['pass_pct']:.1f}%", f"{stats['fail_pct']:.1f}%"])

                # دمج Gender و Section للصفين
                span_commands.append(('SPAN', (0, current_row), (0, current_row+1)))  # Gender
                span_commands.append(('SPAN', (1, current_row), (1, current_row+1)))  # Section
                current_row += 2

            # إجمالي الإناث
            female_stats = self._calculate_section_statistics(female_sections)
            data.append(['Total (Female)', '', 'Number of Students'] +
                       [str(female_stats['grades'][g]) for g in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F']] +
                       [str(female_stats['pass']), str(female_stats['fail'])])
            data.append(['', '', 'Percentage'] +
                       [f"{female_stats['grades_pct'][g]:.1f}%" for g in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F']] +
                       [f"{female_stats['pass_pct']:.1f}%", f"{female_stats['fail_pct']:.1f}%"])

            span_commands.append(('SPAN', (0, current_row), (1, current_row)))  # Total Female gender
            span_commands.append(('SPAN', (0, current_row+1), (1, current_row+1)))  # Total Female percentage
            current_row += 2

        # إنشاء الجدول
        col_widths = [2.5*cm, 2.5*cm, 3*cm] + [1.3*cm]*9 + [1.5*cm]*2
        table = Table(data, colWidths=col_widths)

        style = [
            # الحدود
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#4472C4')),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#4472C4')),

            # ألوان الخلفية - العناوين
            ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#B4C7E7')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#D9E2F3')),

            # ألوان صفوف Total
            ('BACKGROUND', (0, 2), (2, -1), colors.HexColor('#E7E6E6')),  # Default gray

            # محاذاة
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # الخط
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 2), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),

            # دمج الخلايا للعناوين
            ('SPAN', (0, 0), (0, 1)),  # Gender
            ('SPAN', (1, 0), (1, 1)),  # Section
            ('SPAN', (2, 0), (2, 1)),  # Empty column
            ('SPAN', (3, 0), (11, 0)), # Grades header
            ('SPAN', (12, 0), (13, 0)), # Status header
        ]

        # إضافة أوامر الدمج الديناميكية
        style.extend(span_commands)

        # تلوين صفوف Total بلون مميز
        row = 2
        if male_sections:
            male_total_row = row + len(male_sections) * 2
            style.append(('BACKGROUND', (0, male_total_row), (-1, male_total_row+1), colors.HexColor('#FFF2CC')))
            row = male_total_row + 2

        if female_sections:
            female_total_row = row + len(female_sections) * 2
            style.append(('BACKGROUND', (0, female_total_row), (-1, female_total_row+1), colors.HexColor('#FFF2CC')))

        # جعل أرقام Pass و Fail بخط عريض
        style.append(('FONTNAME', (12, 2), (13, -1), 'Helvetica-Bold'))

        table.setStyle(TableStyle(style))

        elements.append(table)

        return elements

    def _get_letter_grade(self, total_mark):
        """تحويل الدرجة العددية إلى حرفية"""
        if total_mark >= 95:
            return 'A+'
        elif total_mark >= 90:
            return 'A'
        elif total_mark >= 85:
            return 'B+'
        elif total_mark >= 80:
            return 'B'
        elif total_mark >= 75:
            return 'C+'
        elif total_mark >= 70:
            return 'C'
        elif total_mark >= 65:
            return 'D+'
        elif total_mark >= 60:
            return 'D'
        else:
            return 'F'

    def _calculate_section_statistics(self, sections):
        """حساب إحصائيات الشعب"""
        stats = {
            'grades': {'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C+': 0, 'C': 0, 'D+': 0, 'D': 0, 'F': 0},
            'grades_pct': {'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C+': 0, 'C': 0, 'D+': 0, 'D': 0, 'F': 0},
            'status': {'Prohibited': 0, 'Dropped': 0, 'Incomplete': 0},
            'status_pct': {'Prohibited': 0, 'Dropped': 0, 'Incomplete': 0},
            'pass': 0,
            'fail': 0,
            'pass_pct': 0,
            'fail_pct': 0
        }

        total_students = 0
        regular_students = 0

        for section in sections:
            for student in section.students:
                total_students += 1

                # حساب الحالات
                status = student.status.value if hasattr(student.status, 'value') else student.status

                # فقط الطلاب المنتظمون يتم احتساب درجاتهم
                if status == 'Regular':
                    regular_students += 1

                    # حساب الدرجة الحرفية من total_mark
                    letter_grade = self._get_letter_grade(student.total_mark)

                    if letter_grade in stats['grades']:
                        stats['grades'][letter_grade] += 1

                    # حساب النجاح والرسوب
                    if letter_grade != 'F':
                        stats['pass'] += 1
                    else:
                        stats['fail'] += 1

        # حساب النسب المئوية (بالنسبة للطلاب المنتظمين فقط)
        if regular_students > 0:
            for grade in stats['grades']:
                stats['grades_pct'][grade] = (stats['grades'][grade] / regular_students) * 100

            stats['pass_pct'] = (stats['pass'] / regular_students) * 100
            stats['fail_pct'] = (stats['fail'] / regular_students) * 100

        return stats

    def _create_clo_assessment_page(self, sections, gender):
        """إنشاء صفحة تقييم المخرجات"""
        elements = []

        # ترتيب الشعب حسب رقم الشعبة
        sorted_sections = sorted(sections, key=lambda s: s.section_number)

        # العنوان
        title_text = f"1. Course Learning Outcomes Assessment Results\n\n({gender} Sections)"
        title = Paragraph(title_text, self.styles['EnglishTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))

        # إنشاء بيانات الجدول
        data = []

        # رأس الجدول - الصف الأول
        num_sections = len(sorted_sections)
        header_row1 = ['', 'CLO Code', 'Target Level', 'Actual Level'] + [''] * (num_sections - 1) + ['']

        # رأس الجدول - الصف الثاني (أرقام الشعب)
        section_headers = [f'Section {s.section_number}' for s in sorted_sections]
        header_row2 = ['', '', ''] + section_headers + ['Total']

        data.append(header_row1)
        data.append(header_row2)

        # قائمة لتتبع الصفوف غير المحققة (لتلوينها بالأحمر)
        not_achieved_rows = []

        # تجميع المخرجات حسب الفئة
        from models.course import CLOCategory

        clos_by_category = {}
        for clo in self.course.clos:
            category = clo.category if hasattr(clo, 'category') and clo.category else None
            if category not in clos_by_category:
                clos_by_category[category] = []
            clos_by_category[category].append(clo)

        # إضافة بيانات المخرجات
        category_map = {
            CLOCategory.KNOWLEDGE: ('1', 'Knowledge and Understanding:'),
            CLOCategory.SKILLS: ('2', 'Skills:'),
            CLOCategory.VALUES: ('3', 'Values:')
        }

        current_row = 2  # نبدأ من الصف 2 (بعد العناوين)

        for category, (num, title) in category_map.items():
            if category in clos_by_category:
                # إضافة صف الفئة - يمتد عبر جميع أعمدة الشعب
                category_row = [num, '', ''] + [title] + [''] * (num_sections - 1) + ['']
                data.append(category_row)
                current_row += 1

                # إضافة المخرجات
                for clo in clos_by_category[category]:
                    # حساب المستوى الفعلي لكل شعبة
                    section_levels = []
                    for section in sorted_sections:
                        level = self._calculate_clo_level(section, clo.code)
                        section_levels.append(f"{level:.1f}%" if level is not None else "N/A")

                    # حساب المجموع باستخدام الوسط الحسابي المرجح
                    total_level = self._calculate_clo_level_total_weighted(sorted_sections, clo.code)
                    total_str = f"{total_level:.1f}%" if total_level is not None else "N/A"

                    # المستوى المستهدف
                    target = sorted_sections[0].clo_target_levels.get(clo.code, clo.target_level) if sorted_sections else clo.target_level
                    target_str = f"{target:.1f}%" if target else "N/A"

                    # التحقق من تحقيق المخرج
                    is_achieved = total_level and total_level >= target
                    if not is_achieved:
                        not_achieved_rows.append(current_row)

                    row = ['', clo.code, target_str] + section_levels + [total_str]
                    data.append(row)
                    current_row += 1

        # إنشاء الجدول - عرض أعمدة ديناميكي
        # 1cm + 2cm + 2.5cm (أول 3 أعمدة) + أعمدة الشعب + 3cm (Total)
        base_width = 1*cm + 2*cm + 2.5*cm + 3*cm
        available_for_sections = 25*cm - base_width
        section_col_width = available_for_sections / num_sections if num_sections > 0 else 3*cm

        col_widths = [1*cm, 2*cm, 2.5*cm] + [section_col_width] * num_sections + [3*cm]
        table = Table(data, colWidths=col_widths)

        # آخر عمود قبل Total
        last_section_col = 3 + num_sections - 1
        total_col = last_section_col + 1

        style = [
            # الحدود
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#4472C4')),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#4472C4')),

            # ألوان الخلفية
            ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#B4C7E7')),

            # محاذاة
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # الخط
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),

            # دمج الخلايا للرأس
            ('SPAN', (3, 0), (last_section_col, 0)),  # Actual Level
            ('SPAN', (total_col, 0), (total_col, 1)),  # Total
        ]

        # دمج خلايا الفئات وتلوينها
        row = 2
        for category in category_map:
            if category in clos_by_category:
                # دمج خلايا عنوان الفئة
                style.append(('SPAN', (3, row), (last_section_col, row)))
                style.append(('BACKGROUND', (0, row), (-1, row), colors.HexColor('#D9E2F3')))
                style.append(('FONTNAME', (0, row), (-1, row), 'Helvetica-Bold'))
                row += 1 + len(clos_by_category[category])

        # تلوين الصفوف التي لم يتحقق فيها المخرج بالأحمر
        for row_num in not_achieved_rows:
            style.append(('BACKGROUND', (0, row_num), (-1, row_num), colors.HexColor('#FFB3B3')))

        table.setStyle(TableStyle(style))

        elements.append(table)

        return elements

    def _calculate_clo_level(self, section, clo_code):
        """حساب المستوى الفعلي لمخرج محدد في شعبة"""
        regular_students = [s for s in section.students if s.status.value == 'Regular']
        if not regular_students:
            return None

        total_achieved = 0
        for student in regular_students:
            # حساب نسبة إنجاز الطالب في هذا المخرج
            clo_percentage = self._calculate_student_clo_percentage(section, student, clo_code)
            target = section.clo_target_levels.get(clo_code, 70)

            if clo_percentage is not None and clo_percentage >= target:
                total_achieved += 1

        return (total_achieved / len(regular_students)) * 100

    def _calculate_clo_level_total(self, sections, clo_code):
        """حساب المستوى الفعلي الإجمالي لمخرج محدد (الطريقة القديمة)"""
        all_regular_students = []
        for section in sections:
            all_regular_students.extend([s for s in section.students if s.status.value == 'Regular'])

        if not all_regular_students:
            return None

        total_achieved = 0
        for section in sections:
            regular_students = [s for s in section.students if s.status.value == 'Regular']
            target = section.clo_target_levels.get(clo_code, 70)

            for student in regular_students:
                clo_percentage = self._calculate_student_clo_percentage(section, student, clo_code)
                if clo_percentage is not None and clo_percentage >= target:
                    total_achieved += 1

        return (total_achieved / len(all_regular_students)) * 100

    def _calculate_clo_level_total_weighted(self, sections, clo_code):
        """
        حساب المستوى الفعلي الإجمالي باستخدام الوسط الحسابي المرجح
        المعادلة: Σ(عدد الطلاب المنتظمين × المستوى الفعلي) / Σ(عدد الطلاب المنتظمين)
        """
        total_weighted_sum = 0.0
        total_regular_students = 0

        for section in sections:
            # عدد الطلاب المنتظمين في الشعبة
            regular_students = [s for s in section.students if s.status.value == 'Regular']
            num_regular = len(regular_students)

            if num_regular > 0:
                # حساب المستوى الفعلي للشعبة
                section_level = self._calculate_clo_level(section, clo_code)

                if section_level is not None:
                    # إضافة إلى المجموع المرجح
                    total_weighted_sum += num_regular * section_level
                    total_regular_students += num_regular

        # حساب الوسط الحسابي المرجح
        if total_regular_students > 0:
            return total_weighted_sum / total_regular_students
        else:
            return None

    def _calculate_student_clo_percentage(self, section, student, clo_code):
        """حساب نسبة إنجاز الطالب في مخرج محدد"""
        # الحصول على درجة الطالب في هذا المخرج
        student_clo_mark = student.clo_marks.get(clo_code, 0)

        # الحصول على الدرجة الكلية لهذا المخرج من المقرر
        clo_total_mark = 0
        for clo in self.course.clos:
            if clo.code == clo_code:
                clo_total_mark = clo.mark
                break

        if clo_total_mark > 0:
            return (student_clo_mark / clo_total_mark) * 100
        return None

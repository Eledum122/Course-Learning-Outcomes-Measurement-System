"""
مولد تقرير قياس مخرجات التعلم - CLO Assessment Report Generator
ينشئ ملف PDF يحتوي على نتائج قياس مخرجات المقرر الدراسي
"""

import os
from datetime import datetime
from typing import Dict, List
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from bidi.algorithm import get_display
import arabic_reshaper

from models import Course, CourseSection, Student, CLO
from translations import t
from utils.report_utils import add_report_header, add_page_number_first, add_page_number_with_watermark


class CLOAssessmentReportGenerator:
    """مولد تقرير قياس مخرجات التعلم"""

    def __init__(self, course: Course, section: CourseSection, language: str = 'ar'):
        """
        تهيئة مولد التقرير

        Args:
            course: كائن المقرر
            section: كائن الشعبة
            language: اللغة (ar أو en)
        """
        self.course = course
        self.section = section
        self.language = language
        self.is_rtl = (language == 'ar')

        # تسجيل الخطوط العربية
        self._register_fonts()

        # إعداد الأنماط
        self.styles = self._create_styles()

        # حساب الإحصائيات
        self._calculate_statistics()

    def _register_fonts(self):
        """تسجيل الخطوط العربية"""
        try:
            font_path = os.path.join('fonts', 'Tajawal-Regular.ttf')
            font_bold_path = os.path.join('fonts', 'Tajawal-Bold.ttf')

            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arabic', font_path))
            if os.path.exists(font_bold_path):
                pdfmetrics.registerFont(TTFont('Arabic-Bold', font_bold_path))
        except Exception as e:
            print(f"Error registering fonts: {e}")

    def _create_styles(self):
        """إنشاء أنماط النصوص"""
        styles = getSampleStyleSheet()

        # نمط العنوان الرئيسي
        styles.add(ParagraphStyle(
            name='ArabicTitle',
            fontName='Arabic-Bold',
            fontSize=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=15,
            leading=24
        ))

        # نمط العنوان الفرعي
        styles.add(ParagraphStyle(
            name='ArabicHeading',
            fontName='Arabic-Bold',
            fontSize=14,
            alignment=TA_RIGHT if self.is_rtl else TA_LEFT,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=10,
            spaceBefore=15,
            leading=18
        ))

        # نمط النص العادي
        styles.add(ParagraphStyle(
            name='ArabicNormal',
            fontName='Arabic',
            fontSize=11,
            alignment=TA_RIGHT if self.is_rtl else TA_LEFT,
            leading=16,
            spaceBefore=5,
            spaceAfter=5
        ))

        # نمط نص الجدول
        styles.add(ParagraphStyle(
            name='ArabicTable',
            fontName='Arabic',
            fontSize=10,
            alignment=TA_CENTER,
            leading=14
        ))

        return styles

    def _reshape_text(self, text: str) -> str:
        """إعادة تشكيل النص العربي للعرض الصحيح"""
        if not self.is_rtl or not text:
            return text
        try:
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped)
        except:
            return text

    def _get_grade_from_percentage(self, percentage):
        """تحويل النسبة المئوية إلى تقدير"""
        if percentage >= 95:
            return 'A+'
        elif percentage >= 90:
            return 'A'
        elif percentage >= 85:
            return 'B+'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 75:
            return 'C+'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 65:
            return 'D+'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'

    def _calculate_statistics(self):
        """حساب إحصائيات الطلاب والمخرجات"""
        # إحصائيات الطلاب حسب الحالة
        self.total_students = len(self.section.students)
        self.regular_students = len([s for s in self.section.students if s.status.value == "Regular"])
        self.dropped_students = len([s for s in self.section.students if s.status.value == "Dropped"])
        self.prohibited_students = len([s for s in self.section.students if s.status.value == "Prohibited"])
        self.incomplete_students = len([s for s in self.section.students if s.status.value == "Incomplete"])

        # حساب توزيع التقديرات
        self.grade_distribution = {
            'A+': 0, 'A': 0, 'B+': 0, 'B': 0,
            'C+': 0, 'C': 0, 'D+': 0, 'D': 0, 'F': 0
        }

        # حساب عدد الناجحين والراسبين من المنتظمين
        self.passed_students = 0
        self.failed_students = 0

        for student in self.section.students:
            if student.status.value == "Regular":
                # حساب النسبة المئوية
                percentage = (student.total_mark / self.course.info.total_mark) * 100
                grade = self._get_grade_from_percentage(percentage)
                self.grade_distribution[grade] += 1

                # حساب النجاح/الرسوب
                if student.passed:
                    self.passed_students += 1
                else:
                    self.failed_students += 1

        # حساب المستوى الفعلي لكل مخرج (CLO)
        self.clo_results = {}

        for clo in self.course.clos:
            # المستوى المستهدف
            target_level = self.section.clo_target_levels.get(clo.code, clo.target_level)

            # حساب عدد الطلاب المنتظمين الذين حققوا 60% فأكثر في هذا المخرج
            regular_students_list = [s for s in self.section.students if s.status.value == "Regular"]

            # الدرجة الكلية للمخرج من جميع الأنشطة (من جدول المواصفات)
            total_clo_mark = 0
            # جمع الدرجات من جداول المواصفات في المواضيع
            if hasattr(self.course, 'topics') and self.course.topics:
                for topic in self.course.topics:
                    if hasattr(topic, 'specifications_table') and topic.specifications_table:
                        # جدول المواصفات بصيغة: {"CLO|Activity": mark}
                        for key, mark in topic.specifications_table.items():
                            parts = key.split('|')
                            if len(parts) == 2:
                                clo_code_in_spec = parts[0]
                                activity_name_in_spec = parts[1]
                                if clo_code_in_spec == clo.code:
                                    total_clo_mark += mark

            if not regular_students_list or total_clo_mark == 0:
                actual_level = 0
                achieved_count = 0
                threshold_mark = 0
            else:
                # معيار النجاح (60% من الدرجة الكلية للمخرج)
                criterion_percentage = clo.criterion_for_success if hasattr(clo, 'criterion_for_success') else 60.0
                threshold_mark = total_clo_mark * (criterion_percentage / 100.0)

                # عد الطلاب الذين حققوا معيار النجاح فأكثر
                achieved_count = 0

                for student in regular_students_list:
                    # حساب مجموع درجات الطالب في هذا المخرج من جميع الأنشطة
                    student_clo_total = student.clo_marks.get(clo.code, 0)

                    if student_clo_total >= threshold_mark:
                        achieved_count += 1

                # حساب المستوى الفعلي = (عدد الطلاب الذين حققوا المعيار ÷ العدد الكلي للمنتظمين) × 100
                actual_level = (achieved_count / len(regular_students_list)) * 100

            # تحديد حالة التحقق
            achieved = actual_level >= target_level

            self.clo_results[clo.code] = {
                'clo': clo,
                'target_level': target_level,
                'actual_level': actual_level,
                'achieved': achieved,
                'total_mark': total_clo_mark,
                'threshold_mark': threshold_mark,
                'achieved_count': achieved_count,
                'total_regular': len(regular_students_list)
            }

    def generate_report(self, output_path: str):
        """
        توليد تقرير PDF

        Args:
            output_path: مسار حفظ الملف
        """
        # إنشاء مستند PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,  # هامش عادي
            bottomMargin=2*cm
        )

        # محتوى التقرير
        story = []

        # إضافة ترويسة التقرير
        add_report_header(story, language=self.language, orientation='portrait')

        # إضافة العناصر
        story.extend(self._create_header())
        story.append(Spacer(1, 0.8*cm))

        # إضافة جدول نتائج الطلاب
        story.extend(self._create_student_results_table())
        story.append(Spacer(1, 0.8*cm))

        # إضافة جدول نتائج المخرجات
        story.extend(self._create_clo_results_table())
        story.append(Spacer(1, 1*cm))

        # بناء المستند مع أرقام الصفحات والعلامة المائية
        doc.build(story, onFirstPage=add_page_number_first, onLaterPages=add_page_number_with_watermark)

    def _create_header(self):
        """إنشاء رأس التقرير"""
        elements = []

        # جدول معلومات المقرر الأساسية
        header_data = [
            [self._reshape_text("Course Title:"), self._reshape_text(self.course.info.course_title)],
            [self._reshape_text("Code:"), self._reshape_text(self.course.info.course_code)],
            [self._reshape_text("Program:"), self._reshape_text(self.course.info.program)],
            [self._reshape_text("Department:"), self._reshape_text(self.course.info.department)],
            [self._reshape_text("Section:"), self._reshape_text(self.section.section_number)],
            [self._reshape_text("Academic Year:"), self._reshape_text(self.section.academic_year)],
            [self._reshape_text("Semester:"), self._reshape_text(self.section.semester.value if hasattr(self.section.semester, 'value') else str(self.section.semester))],
            [self._reshape_text("Course Coordinator:"), self._reshape_text(self.section.course_coordinator)],
            [self._reshape_text("Course Instructor:"), self._reshape_text(self.section.section_instructor)],
            [self._reshape_text("Date:"), self._reshape_text(datetime.now().strftime("%Y-%m-%d"))]
        ]

        header_table = Table(header_data, colWidths=[5*cm, 13*cm])
        header_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Arabic-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 0.8*cm))

        return elements

    def _create_student_results_table(self):
        """إنشاء جدول نتائج الطلاب"""
        elements = []

        # عنوان القسم
        elements.append(Paragraph(
            self._reshape_text("Student Results"),
            self.styles['ArabicHeading']
        ))
        elements.append(Spacer(1, 0.3*cm))

        # بناء جدول بسيط بدون تعقيد الدمج
        # الصف الأول - رؤوس الأعمدة
        headers = [Paragraph(self._reshape_text(""), self.styles['ArabicTable'])]

        # Grades headers
        for grade in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F']:
            headers.append(Paragraph(self._reshape_text(grade), self.styles['ArabicTable']))

        # Status Distribution headers
        for status in ['Prohibited', 'dropped', 'Incomplete', 'Pass', 'Fail']:
            headers.append(Paragraph(self._reshape_text(status), self.styles['ArabicTable']))

        # الصف الثاني - عدد الطلاب
        counts_row = [Paragraph(self._reshape_text("Number of Students"), self.styles['ArabicTable'])]

        # Grades counts
        for grade in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F']:
            count = self.grade_distribution.get(grade, 0)
            counts_row.append(Paragraph(str(count), self.styles['ArabicTable']))

        # Status counts
        counts_row.append(Paragraph(str(self.prohibited_students), self.styles['ArabicTable']))
        counts_row.append(Paragraph(str(self.dropped_students), self.styles['ArabicTable']))
        counts_row.append(Paragraph(str(self.incomplete_students), self.styles['ArabicTable']))
        counts_row.append(Paragraph(str(self.passed_students), self.styles['ArabicTable']))
        counts_row.append(Paragraph(str(self.failed_students), self.styles['ArabicTable']))

        # الصف الثالث - النسب المئوية
        percentage_row = [Paragraph(self._reshape_text("Percentage"), self.styles['ArabicTable'])]

        # Grades percentages
        for grade in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F']:
            count = self.grade_distribution.get(grade, 0)
            percentage = (count / self.regular_students * 100) if self.regular_students > 0 else 0
            percentage_row.append(Paragraph(f"{percentage:.1f}%", self.styles['ArabicTable']))

        # Status percentages
        total_for_status = self.total_students if self.total_students > 0 else 1
        prohibited_pct = (self.prohibited_students / total_for_status) * 100
        dropped_pct = (self.dropped_students / total_for_status) * 100
        incomplete_pct = (self.incomplete_students / total_for_status) * 100
        passed_pct = (self.passed_students / self.regular_students * 100) if self.regular_students > 0 else 0
        failed_pct = (self.failed_students / self.regular_students * 100) if self.regular_students > 0 else 0

        percentage_row.append(Paragraph(f"{prohibited_pct:.1f}%", self.styles['ArabicTable']))
        percentage_row.append(Paragraph(f"{dropped_pct:.1f}%", self.styles['ArabicTable']))
        percentage_row.append(Paragraph(f"{incomplete_pct:.1f}%", self.styles['ArabicTable']))
        percentage_row.append(Paragraph(f"{passed_pct:.1f}%", self.styles['ArabicTable']))
        percentage_row.append(Paragraph(f"{failed_pct:.1f}%", self.styles['ArabicTable']))

        # بناء الجدول
        data = [headers, counts_row, percentage_row]
        col_widths = [2.5*cm] + [1.1*cm]*9 + [1.4*cm]*5

        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # تنسيق الرأس
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#E3F2FD')),
            ('BACKGROUND', (1, 0), (9, 0), colors.HexColor('#1976D2')),
            ('BACKGROUND', (10, 0), (14, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (1, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Arabic-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),

            # تنسيق باقي الصفوف
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#E3F2FD')),
            ('FONTNAME', (0, 1), (-1, -1), 'Arabic'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),

            # المحاذاة
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # الحدود
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1976D2')),

            # المسافات
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))

        # إضافة مربعات التعليقات والتوصيات
        # Comment on Student Results
        comment_title = Paragraph(
            self._reshape_text("Comment on Student Results:"),
            self.styles['ArabicHeading']
        )
        elements.append(comment_title)

        comment_box = Table(
            [[Paragraph("", self.styles['ArabicTable'])]],
            colWidths=[17*cm]
        )
        comment_box.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 30),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 30),
        ]))
        elements.append(comment_box)
        elements.append(Spacer(1, 0.8*cm))

        return elements


    def _create_clo_results_table(self):
        """إنشاء جدول نتائج المخرجات"""
        elements = []

        from models.course import CLOCategory

        # عنوان القسم
        elements.append(Paragraph(
            self._reshape_text("Course Learning Outcomes Assessment Results"),
            self.styles['ArabicHeading']
        ))

        # رأس الجدول باستخدام Paragraph للتحكم بالتفاف النص
        header = [
            Paragraph(self._reshape_text("Course learning Outcomes"), self.styles['ArabicTable']),
            Paragraph(self._reshape_text("PLOs Code"), self.styles['ArabicTable']),
            Paragraph(self._reshape_text("Criterion for success"), self.styles['ArabicTable']),
            Paragraph(self._reshape_text("Target Level"), self.styles['ArabicTable']),
            Paragraph(self._reshape_text("Actual Level"), self.styles['ArabicTable']),
            Paragraph(self._reshape_text("Comment on Assessment Results"), self.styles['ArabicTable'])
        ]

        data = [header]

        # تنظيم المخرجات حسب الفئة
        categories = {
            CLOCategory.KNOWLEDGE: [],
            CLOCategory.SKILLS: [],
            CLOCategory.VALUES: []
        }

        for clo_code in sorted(self.clo_results.keys()):
            result = self.clo_results[clo_code]
            clo = result['clo']
            category = clo.category if hasattr(clo, 'category') else CLOCategory.KNOWLEDGE
            categories[category].append((clo_code, result))

        # عداد لترقيم المخرجات داخل كل فئة
        category_names = {
            CLOCategory.KNOWLEDGE: "Knowledge and Understanding:",
            CLOCategory.SKILLS: "Skills:",
            CLOCategory.VALUES: "Values:"
        }

        category_counter = 1
        for category, clos_list in categories.items():
            if not clos_list:
                continue

            # صف عنوان الفئة
            category_row = [
                Paragraph(self._reshape_text(f"{category_counter} {category_names[category]}"), self.styles['ArabicTable']),
                "", "", "", "", ""
            ]
            data.append(category_row)

            # إضافة المخرجات ضمن الفئة
            clo_counter = 1
            for clo_code, result in clos_list:
                clo = result['clo']

                # تحديد التعليق بناءً على النتيجة
                if result['achieved']:
                    comment = Paragraph(self._reshape_text("Achieved"), self.styles['ArabicTable'])
                else:
                    comment = Paragraph(self._reshape_text("Not Achieved"), self.styles['ArabicTable'])

                # وصف المخرج مع الترقيم (بدون قطع النص)
                clo_desc = f"{category_counter}.{clo_counter} {clo.description}"

                row = [
                    Paragraph(self._reshape_text(clo_desc), self.styles['ArabicTable']),
                    Paragraph(self._reshape_text(clo.aligned_plos if hasattr(clo, 'aligned_plos') and clo.aligned_plos else "-"), self.styles['ArabicTable']),
                    Paragraph(self._reshape_text(f"{clo.criterion_for_success:.0f}%" if hasattr(clo, 'criterion_for_success') else "60%"), self.styles['ArabicTable']),
                    Paragraph(self._reshape_text(f"{result['target_level']:.0f}%"), self.styles['ArabicTable']),
                    Paragraph(self._reshape_text(f"{result['actual_level']:.1f}%"), self.styles['ArabicTable']),
                    comment
                ]

                data.append(row)
                clo_counter += 1

            category_counter += 1

        # إنشاء الجدول بعرض أكبر للأعمدة
        table = Table(data, colWidths=[6.5*cm, 2*cm, 2.2*cm, 1.8*cm, 1.8*cm, 2.7*cm])

        # تنسيق أساسي
        style_commands = [
            ('FONT', (0, 0), (-1, -1), 'Arabic'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTSIZE', (0, 0), (-1, 0), 9),  # حجم خط العناوين
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # محاذاة وصف المخرج لليسار
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Arabic-Bold'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('WORDWRAP', (0, 0), (-1, -1), True),  # تفعيل التفاف النص
        ]

        # تنسيق صفوف عناوين الفئات
        row_idx = 1
        for category, clos_list in categories.items():
            if not clos_list:
                continue

            # دمج الخلايا لعنوان الفئة
            style_commands.append(('SPAN', (0, row_idx), (5, row_idx)))
            style_commands.append(('BACKGROUND', (0, row_idx), (5, row_idx), colors.HexColor('#E3F2FD')))
            style_commands.append(('FONTNAME', (0, row_idx), (0, row_idx), 'Arabic-Bold'))
            style_commands.append(('FONTSIZE', (0, row_idx), (0, row_idx), 10))
            style_commands.append(('ALIGN', (0, row_idx), (0, row_idx), 'LEFT'))

            # تلوين صفوف المخرجات حسب النتيجة
            for i, (clo_code, result) in enumerate(clos_list, start=1):
                current_row = row_idx + i
                if result['achieved']:
                    # أخضر للمحقق
                    style_commands.append(('BACKGROUND', (5, current_row), (5, current_row), colors.HexColor('#C8E6C9')))
                    style_commands.append(('TEXTCOLOR', (5, current_row), (5, current_row), colors.HexColor('#2E7D32')))
                else:
                    # أحمر لغير المحقق
                    style_commands.append(('BACKGROUND', (5, current_row), (5, current_row), colors.HexColor('#FFCDD2')))
                    style_commands.append(('TEXTCOLOR', (5, current_row), (5, current_row), colors.HexColor('#C62828')))

            row_idx += len(clos_list) + 1

        table.setStyle(TableStyle(style_commands))

        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))

        # إضافة Comment on Course Learning Outcomes Results
        comment_title = Paragraph(
            self._reshape_text("Comment on Course Learning Outcomes Results:"),
            self.styles['ArabicHeading']
        )
        elements.append(comment_title)

        comment_box = Table(
            [[Paragraph("", self.styles['ArabicTable'])]],
            colWidths=[17*cm]
        )
        comment_box.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 30),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 30),
        ]))
        elements.append(comment_box)

        return elements

    def _create_recommendations(self):
        """إنشاء قسم التوصيات"""
        elements = []

        # عنوان القسم
        elements.append(Paragraph(
            self._reshape_text("2. Calculation Method Example:"),
            self.styles['ArabicHeading']
        ))

        # إضافة مثال توضيحي على الحساب
        if self.clo_results:
            # اختيار أول مخرج كمثال
            first_clo_code = sorted(self.clo_results.keys())[0]
            result = self.clo_results[first_clo_code]
            clo = result['clo']

            example_text = f"Example: Calculating Actual Level for CLO {first_clo_code}\n\n"
            example_text += f"Step 1: Total marks for this CLO across all activities = {result['total_mark']:.1f} marks\n"

            criterion = clo.criterion_for_success if hasattr(clo, 'criterion_for_success') else 60.0
            example_text += f"Step 2: Criterion for success = {criterion:.0f}% of total marks = {result['threshold_mark']:.1f} marks\n"

            example_text += f"Step 3: Total regular students = {result['total_regular']} students\n"
            example_text += f"Step 4: Students who achieved ≥ {criterion:.0f}% = {result['achieved_count']} students\n\n"

            example_text += f"Calculation:\n"
            example_text += f"Actual Level = ({result['achieved_count']} ÷ {result['total_regular']}) × 100 = {result['actual_level']:.1f}%\n\n"

            example_text += f"Result:\n"
            example_text += f"Target Level = {result['target_level']:.0f}%\n"
            example_text += f"Actual Level = {result['actual_level']:.1f}%\n"
            example_text += f"Status = {'Achieved ✓' if result['achieved'] else 'Not Achieved ✗'}\n"

            elements.append(Paragraph(
                self._reshape_text(example_text),
                self.styles['ArabicNormal']
            ))

        elements.append(Spacer(1, 0.5*cm))

        # عنوان التوصيات
        elements.append(Paragraph(
            self._reshape_text("3. Recommendations:"),
            self.styles['ArabicHeading']
        ))

        # جمع المخرجات غير المحققة
        not_achieved_clos = []
        for clo_code, result in self.clo_results.items():
            if not result['achieved']:
                not_achieved_clos.append((clo_code, result))

        if not_achieved_clos:
            # إنشاء توصيات للمخرجات غير المحققة
            recommendations_text = "Based on the assessment results, the following CLOs did not achieve the target level:\n\n"

            for clo_code, result in not_achieved_clos:
                clo = result['clo']
                gap = result['target_level'] - result['actual_level']
                recommendations_text += f"• {clo_code}: Actual Level ({result['actual_level']:.1f}%) is below Target Level ({result['target_level']:.1f}%) by {gap:.1f}%\n"

            recommendations_text += "\n\nRecommended Actions:\n"
            recommendations_text += "• Review and enhance teaching strategies for the underperforming CLOs\n"
            recommendations_text += "• Provide additional practice materials and exercises\n"
            recommendations_text += "• Consider revising assessment methods to better align with learning outcomes\n"
            recommendations_text += "• Implement remedial sessions for students who are struggling\n"
            recommendations_text += "• Analyze student feedback to identify specific areas of difficulty\n"
        else:
            recommendations_text = "All Course Learning Outcomes have achieved their target levels.\n\n"
            recommendations_text += "Recommended Actions:\n"
            recommendations_text += "• Continue using current teaching methods and strategies\n"
            recommendations_text += "• Consider raising target levels for future semesters to promote continuous improvement\n"
            recommendations_text += "• Share best practices with other course sections or instructors\n"
            recommendations_text += "• Document successful teaching approaches for future reference\n"

        # إضافة مربع فارغ للتوصيات الإضافية
        recommendations_text += "\n\nAdditional Notes:\n"
        recommendations_text += "_" * 100 + "\n"
        recommendations_text += "_" * 100 + "\n"
        recommendations_text += "_" * 100 + "\n"
        recommendations_text += "_" * 100 + "\n"

        elements.append(Paragraph(
            self._reshape_text(recommendations_text),
            self.styles['ArabicNormal']
        ))

        return elements

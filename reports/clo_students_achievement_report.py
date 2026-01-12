"""
تقرير تفصيلي لإنجاز الطلاب في مخرجات التعلم
Detailed CLO Students Achievement Report Generator
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


class CLOStudentsAchievementReport:
    """مولد تقرير إنجاز الطلاب في مخرجات التعلم"""

    def __init__(self, course: Course, sections: List[CourseSection], language: str = 'ar'):
        """
        تهيئة مولد التقرير

        Args:
            course: كائن المقرر
            sections: قائمة الشعب
            language: اللغة (ar أو en)
        """
        self.course = course
        self.sections = sections
        self.language = language
        self.is_rtl = (language == 'ar')

        # تسجيل الخطوط العربية
        self._register_fonts()

        # إعداد الأنماط
        self.styles = self._create_styles()

        # حساب البيانات لكل شعبة
        self._calculate_data()

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
            name='ArabicSubtitle',
            fontName='Arabic-Bold',
            fontSize=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#424242'),
            spaceAfter=10,
            leading=20
        ))

        # نمط النص العادي
        styles.add(ParagraphStyle(
            name='ArabicNormal',
            fontName='Arabic',
            fontSize=11,
            alignment=TA_RIGHT if self.is_rtl else TA_LEFT,
            leading=16
        ))

        # نمط النص بالإنجليزية
        styles.add(ParagraphStyle(
            name='EnglishNormal',
            fontName='Helvetica',
            fontSize=11,
            alignment=TA_LEFT,
            leading=16
        ))

        return styles

    def _reshape_text(self, text: str) -> str:
        """تنسيق النص العربي للعرض الصحيح"""
        if self.is_rtl and text:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        return text

    def _calculate_data(self):
        """حساب البيانات لكل شعبة ومخرج"""
        self.sections_data = {}

        for section in self.sections:
            section_data = {
                'section': section,
                'clo_stats': {},
                'students_by_clo': {}  # الطلاب الذين لم يحققوا كل مخرج
            }

            # الطلاب المنتظمون فقط
            regular_students = [s for s in section.students if s.status.value == "Regular"]

            for clo in self.course.clos:
                # حساب الدرجة الكلية للمخرج
                total_clo_mark = self._get_clo_total_mark(clo.code)

                # المستوى المستهدف
                target_level = section.clo_target_levels.get(clo.code, clo.target_level) if section.clo_target_levels else clo.target_level

                # معيار النجاح
                criterion_percentage = clo.criterion_for_success if hasattr(clo, 'criterion_for_success') else 60.0
                threshold_mark = total_clo_mark * (criterion_percentage / 100.0)

                # تصنيف الطلاب
                achieved_students = []
                not_achieved_students = []

                for student in regular_students:
                    student_clo_total = student.clo_marks.get(clo.code, 0)
                    student_percentage = (student_clo_total / total_clo_mark * 100) if total_clo_mark > 0 else 0

                    student_info = {
                        'student': student,
                        'mark': student_clo_total,
                        'total_mark': total_clo_mark,
                        'percentage': student_percentage,
                        'achieved': student_clo_total >= threshold_mark
                    }

                    if student_clo_total >= threshold_mark:
                        achieved_students.append(student_info)
                    else:
                        not_achieved_students.append(student_info)

                # حفظ الإحصائيات
                section_data['clo_stats'][clo.code] = {
                    'clo': clo,
                    'total_mark': total_clo_mark,
                    'threshold_mark': threshold_mark,
                    'criterion_percentage': criterion_percentage,
                    'target_level': target_level,
                    'achieved_count': len(achieved_students),
                    'not_achieved_count': len(not_achieved_students),
                    'total_students': len(regular_students)
                }

                section_data['students_by_clo'][clo.code] = {
                    'achieved': achieved_students,
                    'not_achieved': not_achieved_students
                }

            self.sections_data[section.section_id] = section_data

    def _get_clo_total_mark(self, clo_code: str) -> float:
        """حساب الدرجة الكلية للمخرج من جدول المواصفات"""
        total_mark = 0
        if hasattr(self.course, 'topics') and self.course.topics:
            for topic in self.course.topics:
                if hasattr(topic, 'specifications_table') and topic.specifications_table:
                    for key, mark in topic.specifications_table.items():
                        parts = key.split('|')
                        if len(parts) == 2 and parts[0] == clo_code:
                            total_mark += mark
        return total_mark

    def generate_report(self, output_path: str):
        """
        توليد تقرير PDF

        Args:
            output_path: مسار حفظ الملف
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,  # هامش عادي
            bottomMargin=1.5*cm
        )

        story = []

        # إضافة ترويسة التقرير
        add_report_header(story, language=self.language, orientation='portrait')

        # العنوان الرئيسي
        story.extend(self._create_header())
        story.append(Spacer(1, 0.5*cm))

        # الجزء الأول: جدول ملخص الإنجاز لجميع الشعب
        story.extend(self._create_summary_section())
        story.append(PageBreak())

        # الجزء الثاني: تفاصيل الطلاب لكل شعبة ومخرج
        story.extend(self._create_details_section())

        # بناء المستند مع أرقام الصفحات والعلامة المائية
        doc.build(story, onFirstPage=add_page_number_first, onLaterPages=add_page_number_with_watermark)
        print(f"[OK] Report generated: {output_path}")

    def _create_header(self):
        """إنشاء رأس التقرير"""
        elements = []

        # العنوان
        title = "تقرير تفصيلي لإنجاز الطلاب في مخرجات التعلم" if self.is_rtl else "Detailed CLO Students Achievement Report"
        elements.append(Paragraph(self._reshape_text(title), self.styles['ArabicTitle']))

        # معلومات المقرر
        course_info = f"{self.course.info.course_code} - {self.course.info.course_title}"
        elements.append(Paragraph(self._reshape_text(course_info), self.styles['ArabicSubtitle']))

        # معلومات الشعب
        for section in self.sections:
            section_info = f"الشعبة: {section.section_number} | {section.academic_year} - {section.semester.value}" if self.is_rtl else \
                          f"Section: {section.section_number} | {section.academic_year} - {section.semester.value}"
            elements.append(Paragraph(self._reshape_text(section_info), self.styles['ArabicNormal']))

            # أستاذ الشعبة
            instructor_label = "أستاذ الشعبة:" if self.is_rtl else "Section Instructor:"
            instructor = section.section_instructor if section.section_instructor else ("غير محدد" if self.is_rtl else "Not Specified")
            instructor_text = f"{instructor_label} {instructor}"
            elements.append(Paragraph(self._reshape_text(instructor_text), self.styles['ArabicNormal']))
            elements.append(Spacer(1, 0.2*cm))

        # التاريخ
        date_label = "تاريخ التقرير:" if self.is_rtl else "Report Date:"
        date_text = f"{date_label} {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        elements.append(Paragraph(self._reshape_text(date_text), self.styles['ArabicNormal']))

        return elements

    def _create_summary_section(self):
        """إنشاء قسم الجدول الملخص"""
        elements = []

        # عنوان القسم
        section_title = "الجزء الأول: ملخص إنجاز المخرجات حسب الشعب" if self.is_rtl else "Part 1: Summary of CLO Achievement by Section"
        elements.append(Paragraph(self._reshape_text(section_title), self.styles['ArabicSubtitle']))
        elements.append(Spacer(1, 0.3*cm))

        # بناء الجدول
        table_data = []

        # رأس الجدول (بدون عمود الشعبة)
        if self.is_rtl:
            header = ['المخرج', 'عدد الطلاب', 'حققوا', 'لم يحققوا', 'نسبة الإنجاز']
        else:
            header = ['CLO', 'Total Students', 'Achieved', 'Not Achieved', 'Achievement %']

        header = [self._reshape_text(h) for h in header]
        table_data.append(header)

        # صفوف البيانات
        for section_id, section_data in self.sections_data.items():
            section = section_data['section']

            for clo_code in sorted(section_data['clo_stats'].keys()):
                stats = section_data['clo_stats'][clo_code]
                achievement_pct = (stats['achieved_count'] / stats['total_students'] * 100) if stats['total_students'] > 0 else 0

                row = [
                    clo_code,
                    str(stats['total_students']),
                    str(stats['achieved_count']),
                    str(stats['not_achieved_count']),
                    f"{achievement_pct:.1f}%"
                ]
                table_data.append(row)

        # إنشاء الجدول (بدون عمود الشعبة)
        table = Table(table_data, colWidths=[3*cm, 3*cm, 2.5*cm, 2.5*cm, 3*cm])

        # تنسيق الجدول
        table.setStyle(TableStyle([
            # رأس الجدول
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Arabic-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),

            # بيانات الجدول
            ('FONTNAME', (0, 1), (-1, -1), 'Arabic'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),

            # الحدود
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),

            # ألوان متناوبة للصفوف
            *[('BACKGROUND', (0, i), (-1, i), colors.HexColor('#E3F2FD'))
              for i in range(1, len(table_data), 2)],

            # تلوين حسب نسبة الإنجاز (العمود الأخير - الآن رقم 4)
            *[('BACKGROUND', (4, i), (4, i),
               colors.HexColor('#C8E6C9') if float(table_data[i][4].strip('%')) >= 80
               else colors.HexColor('#FFECB3') if float(table_data[i][4].strip('%')) >= 60
               else colors.HexColor('#FFCDD2'))
              for i in range(1, len(table_data))],
        ]))

        elements.append(table)

        # مفتاح الألوان
        elements.append(Spacer(1, 0.3*cm))
        legend_text = "مفتاح الألوان: أخضر (≥80%) | أصفر (60-79%) | أحمر (<60%)" if self.is_rtl else "Color Key: Green (≥80%) | Yellow (60-79%) | Red (<60%)"
        elements.append(Paragraph(self._reshape_text(legend_text), self.styles['ArabicNormal']))

        return elements

    def _create_details_section(self):
        """إنشاء قسم التفاصيل للطلاب الذين لم يحققوا كل مخرج"""
        elements = []

        # عنوان القسم
        section_title = "الجزء الثاني: الطلاب الذين لم يحققوا المخرجات" if self.is_rtl else "Part 2: Students Who Did Not Achieve CLOs"
        elements.append(Paragraph(self._reshape_text(section_title), self.styles['ArabicSubtitle']))
        elements.append(Spacer(1, 0.5*cm))

        # لكل شعبة
        for section_id, section_data in self.sections_data.items():
            section = section_data['section']

            # عنوان الشعبة
            section_header = f"الشعبة {section.section_number} - {section.academic_year} - {section.semester.value}" if self.is_rtl else f"Section {section.section_number} - {section.academic_year} - {section.semester.value}"
            elements.append(Paragraph(self._reshape_text(section_header), self.styles['ArabicSubtitle']))
            elements.append(Spacer(1, 0.3*cm))

            # لكل مخرج
            for clo_code in sorted(section_data['students_by_clo'].keys()):
                clo_students = section_data['students_by_clo'][clo_code]
                not_achieved = clo_students['not_achieved']
                stats = section_data['clo_stats'][clo_code]

                # عنوان المخرج
                clo_title = f"المخرج {clo_code} - {stats['clo'].description}" if self.is_rtl else f"CLO {clo_code} - {stats['clo'].description}"
                elements.append(Paragraph(self._reshape_text(clo_title), self.styles['ArabicNormal']))

                # معلومات المخرج
                clo_info = f"الدرجة الكلية: {stats['total_mark']:.1f} | معيار النجاح: {stats['criterion_percentage']:.0f}% ({stats['threshold_mark']:.2f} درجة)" if self.is_rtl else f"Total Mark: {stats['total_mark']:.1f} | Success Criterion: {stats['criterion_percentage']:.0f}% ({stats['threshold_mark']:.2f} points)"
                elements.append(Paragraph(self._reshape_text(clo_info), self.styles['ArabicNormal']))
                elements.append(Spacer(1, 0.2*cm))

                if not not_achieved:
                    # لا يوجد طلاب لم يحققوا المخرج
                    msg = "[OK] جميع الطلاب حققوا هذا المخرج" if self.is_rtl else "[OK] All students achieved this CLO"
                    elements.append(Paragraph(self._reshape_text(msg), self.styles['ArabicNormal']))
                else:
                    # جدول الطلاب الذين لم يحققوا المخرج
                    table_data = []

                    # رأس الجدول (بدون اسم الطالب)
                    if self.is_rtl:
                        header = ['#', 'الرقم الجامعي', 'الدرجة', 'من', 'النسبة %']
                    else:
                        header = ['#', 'Student ID', 'Mark', 'Out of', 'Percentage']

                    header = [self._reshape_text(h) for h in header]
                    table_data.append(header)

                    # صفوف الطلاب (بدون الاسم)
                    for idx, student_info in enumerate(not_achieved, 1):
                        student = student_info['student']
                        row = [
                            str(idx),
                            student.student_id,
                            f"{student_info['mark']:.2f}",
                            f"{student_info['total_mark']:.1f}",
                            f"{student_info['percentage']:.1f}%"
                        ]
                        table_data.append(row)

                    # إنشاء الجدول (بدون عمود الاسم)
                    table = Table(table_data, colWidths=[1.5*cm, 4*cm, 2.5*cm, 2.5*cm, 3*cm])

                    # تنسيق الجدول
                    table.setStyle(TableStyle([
                        # رأس الجدول
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D32F2F')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('FONTNAME', (0, 0), (-1, 0), 'Arabic-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

                        # بيانات الجدول
                        ('FONTNAME', (0, 1), (-1, -1), 'Arabic'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),  # جميع الأعمدة في المنتصف

                        # الحدود
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('BOX', (0, 0), (-1, -1), 1.5, colors.black),

                        # ألوان متناوبة
                        *[('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFEBEE'))
                          for i in range(1, len(table_data), 2)],
                    ]))

                    elements.append(table)

                elements.append(Spacer(1, 0.5*cm))

            # فاصل بين الشعب
            if section_id != list(self.sections_data.keys())[-1]:
                elements.append(PageBreak())

        return elements

"""
مولد تقرير المرحلة الأولى - Stage 1 Report Generator
ينشئ ملف PDF قابل للطباعة على ورقة A4 يحتوي على معلومات المقرر
"""

import os
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from bidi.algorithm import get_display
import arabic_reshaper

from models.course import Course, CLOCategory
from translations import t
from utils.report_utils import add_report_header, add_page_number_first, add_page_number_with_watermark


class Stage1ReportGenerator:
    """مولد تقرير المرحلة الأولى"""

    def __init__(self, course: Course, language: str = 'ar'):
        """
        تهيئة مولد التقرير

        Args:
            course: كائن المقرر
            language: اللغة (ar أو en)
        """
        self.course = course
        self.language = language
        self.is_rtl = (language == 'ar')

        # تسجيل الخطوط العربية
        self._register_fonts()

        # إعداد الأنماط
        self.styles = self._create_styles()

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
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=12,
            leading=20
        ))

        # نمط العنوان الفرعي
        styles.add(ParagraphStyle(
            name='ArabicHeading',
            fontName='Arabic-Bold',
            fontSize=12,
            alignment=TA_RIGHT if self.is_rtl else TA_LEFT,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=8,
            spaceBefore=12,
            leading=16
        ))

        # نمط النص العادي
        styles.add(ParagraphStyle(
            name='ArabicNormal',
            fontName='Arabic',
            fontSize=10,
            alignment=TA_RIGHT if self.is_rtl else TA_LEFT,
            leading=14
        ))

        # نمط نص الجدول
        styles.add(ParagraphStyle(
            name='ArabicTable',
            fontName='Arabic',
            fontSize=9,
            alignment=TA_CENTER,
            leading=12
        ))

        return styles

    def _reshape_text(self, text: str) -> str:
        """
        إعادة تشكيل النص العربي للعرض الصحيح في PDF

        Args:
            text: النص المراد تشكيله

        Returns:
            النص المشكّل
        """
        if not text or not self.is_rtl:
            return text

        try:
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception:
            return text

    def generate_report(self, output_path: str) -> bool:
        """
        توليد تقرير PDF

        Args:
            output_path: مسار الملف الناتج

        Returns:
            True إذا نجح التوليد، False عند الفشل
        """
        try:
            # إنشاء مجلد التقارير إذا لم يكن موجوداً
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # إنشاء المستند
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm,
                title=self._reshape_text("تقرير المقرر - المرحلة الأولى")
            )

            # بناء محتوى التقرير
            story = []

            # إضافة ترويسة التقرير
            add_report_header(story, language=self.language, orientation='portrait')

            # العنوان الرئيسي
            story.append(self._create_title())
            story.append(Spacer(1, 0.5*cm))

            # معلومات المقرر
            story.append(self._create_course_info_section())
            story.append(Spacer(1, 0.5*cm))

            # نواتج التعلم
            if self.course.clos:
                story.append(self._create_clos_section())
                story.append(Spacer(1, 0.5*cm))

            # موضوعات المقرر
            if self.course.topics:
                story.append(self._create_topics_section())
                story.append(Spacer(1, 0.5*cm))

            # أنشطة التقييم
            if self.course.activities:
                story.append(self._create_activities_section())

            # بناء المستند مع أرقام الصفحات والعلامة المائية
            doc.build(story, onFirstPage=add_page_number_first, onLaterPages=add_page_number_with_watermark)
            return True

        except Exception as e:
            print(f"Error generating report: {e}")
            return False

    def _create_title(self):
        """إنشاء العنوان الرئيسي"""
        title_text = "تقرير المقرر الدراسي - المرحلة الأولى" if self.is_rtl else "Course Report - Stage 1"
        return Paragraph(self._reshape_text(title_text), self.styles['ArabicTitle'])

    def _create_course_info_section(self):
        """إنشاء قسم معلومات المقرر"""
        info = self.course.info

        # البيانات
        data = []

        # العنوان
        header_text = "معلومات المقرر" if self.is_rtl else "Course Information"
        data.append([Paragraph(self._reshape_text(header_text), self.styles['ArabicHeading']), ''])

        # الحقول
        fields = [
            ('كود المقرر:', info.course_code, 'Course Code:', info.course_code),
            ('اسم المقرر:', info.course_title, 'Course Title:', info.course_title),
            ('الإصدار:', info.version, 'Version:', info.version),
            ('القسم:', info.department, 'Department:', info.department),
            ('البرنامج:', info.program, 'Program:', info.program),
            ('الكلية:', info.faculty, 'Faculty:', info.faculty),
            ('العام الأكاديمي:', info.academic_year, 'Academic Year:', info.academic_year),
            ('التاريخ:', info.date, 'Date:', info.date),
        ]

        for ar_label, ar_value, en_label, en_value in fields:
            if self.is_rtl:
                label = self._reshape_text(ar_label)
                value = self._reshape_text(ar_value) if ar_value else ''
            else:
                label = en_label
                value = en_value if en_value else ''

            data.append([
                Paragraph(f'<b>{label}</b>', self.styles['ArabicNormal']),
                Paragraph(value, self.styles['ArabicNormal'])
            ])

        # إنشاء الجدول
        col_widths = [5*cm, 12*cm] if self.is_rtl else [5*cm, 12*cm]
        table = Table(data, colWidths=col_widths)

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E3F2FD')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT' if self.is_rtl else 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('SPAN', (0, 0), (-1, 0)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        return table

    def _create_clos_section(self):
        """إنشاء قسم نواتج التعلم"""
        data = []

        # العنوان
        header_text = "نواتج التعلم للمقرر (CLOs)" if self.is_rtl else "Course Learning Outcomes (CLOs)"
        headers = ['الوصف', 'الفئة', 'الكود'] if self.is_rtl else ['Code', 'Category', 'Description']

        data.append([Paragraph(self._reshape_text(header_text), self.styles['ArabicHeading']), '', ''])
        data.append([Paragraph(self._reshape_text(h), self.styles['ArabicTable']) for h in headers])

        # نواتج التعلم
        for clo in self.course.clos:
            category_ar = {
                'Knowledge': 'المعرفة',
                'Skills': 'المهارات',
                'Values': 'القيم'
            }.get(clo.category.value if isinstance(clo.category, CLOCategory) else clo.category, clo.category)

            if self.is_rtl:
                row = [
                    Paragraph(self._reshape_text(clo.description), self.styles['ArabicTable']),
                    Paragraph(self._reshape_text(category_ar), self.styles['ArabicTable']),
                    Paragraph(self._reshape_text(clo.code), self.styles['ArabicTable'])
                ]
            else:
                category_en = clo.category.value if isinstance(clo.category, CLOCategory) else clo.category
                row = [
                    Paragraph(clo.code, self.styles['ArabicTable']),
                    Paragraph(category_en, self.styles['ArabicTable']),
                    Paragraph(clo.description, self.styles['ArabicTable'])
                ]

            data.append(row)

        # إنشاء الجدول
        col_widths = [9*cm, 4*cm, 4*cm] if self.is_rtl else [4*cm, 4*cm, 9*cm]
        table = Table(data, colWidths=col_widths)

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8EAF6')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#9C27B0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#6A1B9A')),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 1), (-1, -1), 0.5, colors.grey),
            ('SPAN', (0, 0), (-1, 0)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        return table

    def _create_topics_section(self):
        """إنشاء قسم موضوعات المقرر"""
        data = []

        # العنوان
        header_text = "موضوعات المقرر" if self.is_rtl else "Course Topics"
        headers = ['ملاحظات', 'الدرجة', 'ساعات الاتصال', 'العنوان', 'رقم'] if self.is_rtl else ['No.', 'Title', 'Hours', 'Mark', 'Remarks']

        data.append([Paragraph(self._reshape_text(header_text), self.styles['ArabicHeading']), '', '', '', ''])
        data.append([Paragraph(self._reshape_text(h), self.styles['ArabicTable']) for h in headers])

        # الموضوعات
        for topic in self.course.topics:
            if self.is_rtl:
                row = [
                    Paragraph(self._reshape_text(topic.remark), self.styles['ArabicTable']),
                    Paragraph(str(topic.mark), self.styles['ArabicTable']),
                    Paragraph(str(topic.contact_hours), self.styles['ArabicTable']),
                    Paragraph(self._reshape_text(topic.title), self.styles['ArabicTable']),
                    Paragraph(str(topic.number), self.styles['ArabicTable'])
                ]
            else:
                row = [
                    Paragraph(str(topic.number), self.styles['ArabicTable']),
                    Paragraph(topic.title, self.styles['ArabicTable']),
                    Paragraph(str(topic.contact_hours), self.styles['ArabicTable']),
                    Paragraph(str(topic.mark), self.styles['ArabicTable']),
                    Paragraph(topic.remark, self.styles['ArabicTable'])
                ]

            data.append(row)

        # إنشاء الجدول
        col_widths = [4*cm, 2.5*cm, 3*cm, 5*cm, 2.5*cm] if self.is_rtl else [2.5*cm, 5*cm, 3*cm, 2.5*cm, 4*cm]
        table = Table(data, colWidths=col_widths)

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFF8E1')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#FBC02D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#F57F17')),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 1), (-1, -1), 0.5, colors.grey),
            ('SPAN', (0, 0), (-1, 0)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        return table

    def _create_activities_section(self):
        """إنشاء قسم أنشطة التقييم"""
        data = []

        # العنوان
        header_text = "أنشطة التقييم" if self.is_rtl else "Assessment Activities"
        headers = ['التوقيت', 'النسبة %', 'الدرجة', 'النشاط'] if self.is_rtl else ['Activity', 'Mark', 'Percentage %', 'Timing']

        data.append([Paragraph(self._reshape_text(header_text), self.styles['ArabicHeading']), '', '', ''])
        data.append([Paragraph(self._reshape_text(h), self.styles['ArabicTable']) for h in headers])

        # الأنشطة
        for activity in self.course.activities:
            if self.is_rtl:
                row = [
                    Paragraph(self._reshape_text(activity.timing), self.styles['ArabicTable']),
                    Paragraph(f"{activity.percentage:.1f}", self.styles['ArabicTable']),
                    Paragraph(str(activity.mark), self.styles['ArabicTable']),
                    Paragraph(self._reshape_text(activity.name), self.styles['ArabicTable'])
                ]
            else:
                row = [
                    Paragraph(activity.name, self.styles['ArabicTable']),
                    Paragraph(str(activity.mark), self.styles['ArabicTable']),
                    Paragraph(f"{activity.percentage:.1f}", self.styles['ArabicTable']),
                    Paragraph(activity.timing, self.styles['ArabicTable'])
                ]

            data.append(row)

        # إنشاء الجدول
        col_widths = [4*cm, 3*cm, 3*cm, 7*cm] if self.is_rtl else [7*cm, 3*cm, 3*cm, 4*cm]
        table = Table(data, colWidths=col_widths)

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8F5E9')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#43A047')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 1), (-1, -1), 0.5, colors.grey),
            ('SPAN', (0, 0), (-1, 0)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        return table

"""
مولد تقرير ورقة النشاط - Activity Sheet Generator
ينشئ ملف PDF قابل للطباعة على ورقة A4 يحتوي على جدول لتوزيع النشاط على المواضيع والمخرجات
"""

import os
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from bidi.algorithm import get_display
import arabic_reshaper

from models.course import Course


class ActivitySheetGenerator:
    """مولد تقرير ورقة النشاط"""

    def __init__(self, course: Course, activity_name: str, language: str = 'en'):
        """
        تهيئة مولد التقرير

        Args:
            course: كائن المقرر
            activity_name: اسم النشاط
            language: اللغة (ar أو en)
        """
        self.course = course
        self.activity_name = activity_name
        self.language = language
        self.is_rtl = (language == 'ar')

        # البحث عن النشاط
        self.activity = None
        for act in course.activities:
            if act.name == activity_name:
                self.activity = act
                break

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

        # نمط للنصوص العربية
        styles.add(ParagraphStyle(
            name='ArabicTitle',
            fontName='Arabic-Bold',
            fontSize=14,
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#1976D2'),
            leading=18
        ))

        styles.add(ParagraphStyle(
            name='ArabicNormal',
            fontName='Arabic',
            fontSize=10,
            alignment=TA_RIGHT,
            leading=14
        ))

        # نمط للنصوص الإنجليزية
        styles.add(ParagraphStyle(
            name='EnglishTitle',
            fontName='Helvetica-Bold',
            fontSize=14,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#D4AF37'),
            leading=18
        ))

        styles.add(ParagraphStyle(
            name='EnglishNormal',
            fontName='Helvetica',
            fontSize=10,
            alignment=TA_LEFT,
            leading=14
        ))

        styles.add(ParagraphStyle(
            name='CenterBold',
            fontName='Helvetica-Bold',
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#D4AF37'),
            leading=20
        ))

        return styles

    def _reshape_arabic(self, text):
        """إعادة تشكيل النص العربي للعرض الصحيح في PDF"""
        if not text:
            return ""
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)

    def _create_header(self):
        """إنشاء ترويسة التقرير مع الشعارات"""
        elements = []

        # جدول الترويسة (3 أعمدة: معلومات عربي | شعارات | معلومات إنجليزي)
        header_data = []

        # الصف الأول: العناوين الأساسية
        arabic_uni = self._reshape_arabic("جامعة تبوك")
        arabic_faculty = self._reshape_arabic("كلية العلوم")
        arabic_dept = self._reshape_arabic("قسم الإحصاء")

        english_uni = Paragraph("University of Tabuk", self.styles['EnglishNormal'])
        english_faculty = Paragraph("<font color='#D4AF37'><b>Faculty of Science</b></font>", self.styles['EnglishNormal'])
        english_dept = Paragraph("<font color='#D4AF37'><b>Department of Statistics</b></font>", self.styles['EnglishNormal'])

        # النصوص العربية (العمود الأيمن)
        arabic_cell = f"""
        <para align='right'>
        <font name='Arabic-Bold' size='10'>{arabic_uni}</font><br/>
        <font name='Arabic-Bold' size='10' color='#D4AF37'>{arabic_faculty}</font><br/>
        <font name='Arabic-Bold' size='10' color='#D4AF37'>{arabic_dept}</font>
        </para>
        """

        # الشعارات (العمود الأوسط) - سنضع مسافة فارغة حالياً
        logo_cell = ""

        # النصوص الإنجليزية (العمود الأيسر)
        english_cell_text = [english_uni, english_faculty, english_dept]

        header_data.append([
            Paragraph(arabic_cell, self.styles['ArabicNormal']),
            logo_cell,
            english_cell_text
        ])

        header_table = Table(header_data, colWidths=[6*cm, 7*cm, 6*cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 0.3*cm))

        # خط فاصل
        line_table = Table([['']], colWidths=[19*cm])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#1976D2')),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 0.5*cm))

        return elements

    def _create_title(self):
        """إنشاء عنوان التقرير"""
        elements = []

        # العنوان الرئيسي بتنسيق خاص
        activity_display = self.activity_name if self.activity_name else "Activity 1"
        course_code = self.course.info.course_code if self.course.info.course_code else "Course Code"

        title_text = f"<b>{activity_display} Sheet – {course_code}</b>"
        title = Paragraph(title_text, self.styles['CenterBold'])

        # جدول لتنسيق العنوان
        title_data = [[title]]
        title_table = Table(title_data, colWidths=[12*cm])
        title_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#1976D2')),
        ]))

        elements.append(title_table)
        elements.append(Spacer(1, 0.8*cm))

        return elements

    def _create_activity_table(self):
        """إنشاء جدول النشاط"""
        elements = []

        if not self.activity:
            # إذا لم يتم العثور على النشاط، إنشاء جدول فارغ
            data = [
                ['No', 'List of Topics', 'CLO', 'Mark'],
                ['1', '', '', ''],
                ['2', '', '', ''],
                ['', '', '', ''],
                ['', '', '', ''],
                [{'content': 'Total', 'span': (0, 2)}, '', 'Total', '']
            ]

            col_widths = [2*cm, 10*cm, 3*cm, 3*cm]

        else:
            # بناء الجدول بناءً على بيانات المقرر
            data = [
                ['No', 'List of Topics', 'CLO', 'Mark']
            ]

            # إضافة صفوف المواضيع (فقط التي تحتوي على درجات لهذا النشاط)
            topic_counter = 0
            for topic in self.course.topics:
                # الحصول على المخرج المرتبط بهذا النشاط في هذا الموضوع
                clo_text = ""
                mark_text = ""
                has_marks = False

                # البحث في specifications_table
                if hasattr(topic, 'specifications_table') and self.activity:
                    for clo in self.course.clos:
                        # التحقق من أن النشاط يقيس هذا المخرج
                        if hasattr(self.activity, 'measures_clos') and clo.code in self.activity.measures_clos:
                            key = f"{clo.code}|{self.activity.name}"
                            mark = topic.specifications_table.get(key, 0)
                            if mark > 0:
                                has_marks = True
                                if clo_text:
                                    clo_text += f"\n{clo.code}"
                                    mark_text += f"\n{mark:.0f}"
                                else:
                                    clo_text = clo.code
                                    mark_text = f"{mark:.0f}"

                # إضافة الموضوع فقط إذا كان له درجات في هذا النشاط
                if has_marks:
                    topic_counter += 1
                    # استخدام عنوان الموضوع المخزن
                    topic_name = topic.title if hasattr(topic, 'title') and topic.title else f"Topic {topic.number}"
                    data.append([
                        str(topic_counter),
                        topic_name,
                        clo_text,
                        mark_text
                    ])

            # صف المجموع
            total_mark = self.activity.mark if self.activity else 0
            data.append(['Total', '', '', f'{total_mark:.0f}'])

            col_widths = [2*cm, 10*cm, 3*cm, 3*cm]

        # إنشاء الجدول
        table = Table(data, colWidths=col_widths, repeatRows=1)

        # تنسيق الجدول
        table_style = [
            # تنسيق الهيدر
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C8E6C9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),

            # تنسيق الخلايا
            ('ALIGN', (0, 1), (0, -2), 'CENTER'),  # عمود No
            ('ALIGN', (1, 1), (1, -2), 'LEFT'),    # عمود Topics
            ('ALIGN', (2, 1), (-1, -2), 'CENTER'), # أعمدة CLO و Mark
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),

            # صف المجموع
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#C8E6C9')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('ALIGN', (0, -1), (-2, -1), 'CENTER'),  # دمج جميع الأعمدة عدا الأخير
            ('ALIGN', (-1, -1), (-1, -1), 'CENTER'),  # عمود الدرجة
            ('SPAN', (0, -1), (-2, -1)),  # دمج من العمود الأول إلى ما قبل الأخير

            # الحدود
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEWIDTH', (0, 0), (-1, 0), 1.5),
            ('LINEWIDTH', (0, -1), (-1, -1), 1.5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]

        table.setStyle(TableStyle(table_style))
        elements.append(table)

        return elements

    def generate(self, output_path: str) -> bool:
        """
        توليد تقرير PDF

        Args:
            output_path: مسار ملف الإخراج

        Returns:
            True إذا تم التوليد بنجاح، False خلاف ذلك
        """
        try:
            # إنشاء المستند
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=1.5*cm,
                leftMargin=1.5*cm,
                topMargin=1.5*cm,
                bottomMargin=1.5*cm
            )

            # بناء محتويات المستند
            story = []

            # الترويسة
            story.extend(self._create_header())

            # العنوان
            story.extend(self._create_title())

            # الجدول
            story.extend(self._create_activity_table())

            # بناء المستند
            doc.build(story)

            return True

        except Exception as e:
            print(f"Error generating activity sheet: {e}")
            import traceback
            traceback.print_exc()
            return False


def generate_activity_sheet(course: Course, activity_name: str, output_path: str, language: str = 'en') -> bool:
    """
    دالة مساعدة لتوليد تقرير ورقة النشاط

    Args:
        course: كائن المقرر
        activity_name: اسم النشاط
        output_path: مسار ملف الإخراج
        language: اللغة (ar أو en)

    Returns:
        True إذا تم التوليد بنجاح، False خلاف ذلك
    """
    generator = ActivitySheetGenerator(course, activity_name, language)
    return generator.generate(output_path)
